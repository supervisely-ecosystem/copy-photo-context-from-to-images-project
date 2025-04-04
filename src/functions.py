import os
from uuid import uuid4

import src.globals as g
import supervisely as sly
from supervisely.api.module_api import ApiField


def recreate_ds_tree(api: sly.Api, src_project_id: int, dst_project_id: int):
    sly.logger.info(f"Checking dataset trees: {src_project_id = }, {dst_project_id = }")
    input_ds_tree = g.api.dataset.get_tree(src_project_id)
    output_ds_tree = g.api.dataset.get_tree(dst_project_id)

    input_datasets = {}
    output_datasets = {}

    def _recreate_ds_tree(input_tree: dict, output_tree: dict, parent_id: int = None):
        """Recursively recreate dataset tree from input project to output project."""
        for ds, children in input_tree.items():
            input_datasets[ds.id] = ds
            if ds.name not in [d.name for d in output_tree.keys()]:
                lbl_ds = api.dataset.create(dst_project_id, ds.name, parent_id=parent_id)
                sly.logger.info(f"Created dataset {lbl_ds.name}")
                # get ds info again to get hashable object (workaround, need to be fixed in SDK)
                lbl_ds = api.dataset.get_info_by_name(dst_project_id, ds.name, parent_id=parent_id)
                output_tree[lbl_ds] = {}
            else:
                for lbl_ds in output_tree.keys():
                    if ds.name == lbl_ds.name:
                        break

            output_datasets[ds.id] = lbl_ds
            if children:
                for child in children:
                    _recreate_ds_tree(child, output_tree[lbl_ds], lbl_ds.id)

    _recreate_ds_tree(input_ds_tree, output_ds_tree)
    return input_datasets, output_datasets


def process_dataset(api: sly.Api, src_ds: sly.DatasetInfo, dst_ds: sly.DatasetInfo):
    # * 1. Download Annotation
    temp_ds_dir_name = f"{src_ds.name}_{uuid4().hex}"
    temp_ds_dir = os.path.join(g.app_data, temp_ds_dir_name)
    sly.fs.mkdir(temp_ds_dir)
    hashs, names, metas = [], [], []

    pointclouds = api.pointcloud_episode.get_list(src_ds.id)
    tqdm = sly.tqdm_sly(
        desc=f"Processing dataset {src_ds.name}",
        total=len(pointclouds),
    )
    for pointcloud_info in pointclouds:
        related_images_path = os.path.join(temp_ds_dir, pointcloud_info.name)
        sly.fs.mkdir(related_images_path)
        try:
            related_images = api.pointcloud_episode.get_list_related_images(pointcloud_info.id)
        except Exception as e:
            sly.logger.info(
                "INFO FOR DEBUGGING",
                extra={
                    "project_id": src_ds.project_id,
                    "dataset_id": src_ds.id,
                    "pointcloud_id": pointcloud_info.id,
                    "pointcloud_name": pointcloud_info.name,
                },
            )
            raise e

        for rimage_info in related_images:
            hashs.append(rimage_info[ApiField.HASH])
            name = rimage_info[ApiField.NAME]
            if not sly.image.has_valid_ext(name):
                new_name = sly.fs.get_file_name(name)  # to fix cases like .png.json
                if sly.image.has_valid_ext(new_name):
                    name = new_name
                    rimage_info[ApiField.NAME] = name
                else:
                    raise RuntimeError(
                        "Something wrong with photo context filenames. Please, contact support"
                    )

            save_name = f"{pointcloud_info.id}_{name}"

            img_meta = {
                ApiField.POINTCLOUD_ID: pointcloud_info.id,
                "deviceId": rimage_info["meta"]["deviceId"],
                ApiField.META: rimage_info,
            }

            names.append(save_name)
            metas.append(img_meta)

        tqdm.update(1)

    # * 2. Upload images
    img_infos = api.image.upload_hashes(dst_ds.id, names, hashs, metas=metas)
    sly.logger.info(f"Uploaded {len(img_infos)} images to dataset {dst_ds.name}")
