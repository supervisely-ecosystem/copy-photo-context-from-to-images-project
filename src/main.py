import src.functions as f
import src.globals as g
import supervisely as sly


def main():
    # * 1. Get src project and dataset infos
    src_project = g.api.project.get_info_by_id(g.project_id)
    if src_project is None:
        raise Exception(f"Project with id={g.project_id} not found")
    if g.dataset_id:
        src_dataset = g.api.dataset.get_info_by_id(g.dataset_id)
        if src_dataset is None:
            raise Exception(f"Dataset with id={g.dataset_id} not found")
        src_datasets = [src_dataset]
        src_datasets += g.api.dataset.get_nested(g.project_id, g.dataset_id)
    else:
        src_datasets = g.api.dataset.get_list(g.project_id, recursive=True)

    # * 2. Create dst project and datasets
    dst_project = g.api.project.create(
        g.workspace_id,
        f"{src_project.name} (Photo Context)",
        sly.ProjectType.IMAGES,
        description=f"Photo Context from project ID:{src_project.id}",
        change_name_if_conflict=True,
    )
    src_datasets, dst_datasets = f.recreate_ds_tree(g.api, src_project.id, dst_project.id)

    # * 3. Process each dataset
    for src_ds_id, src_ds in src_datasets.items():
        dst_ds = dst_datasets[src_ds_id]

        f.process_dataset(g.api, src_ds, dst_ds)

    # * 4. Set output project
    g.api.task.set_output_project(g.task_id, dst_project.id, dst_project.name)

    # * 5. Clean app_data directory
    sly.fs.clean_dir(g.app_data)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
