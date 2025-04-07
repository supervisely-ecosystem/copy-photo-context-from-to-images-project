<div align="center" markdown>

# Copy Photo Context from Pointclouds to Images Project

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Use">How To Use</a> •
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/copy-photo-context-from-to-images-project)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest)](https://img.shields.io/github/v/release/supervisely-ecosystem/copy-photo-context-from-to-images-project)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/copy-photo-context-from-to-images-project.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/copy-photo-context-from-to-images-project.png)](https://supervisely.com)

</div>

# Overview

This app extracts photo context (related images) from point cloud projects and creates a separate images project. It works with both regular point cloud projects and point cloud episodes, preserving the original dataset structure and maintaining valuable metadata from the source project.

💫 The app is a part of the workflow to apply image-based neural networks to point cloud data. By extracting images from point clouds, users can leverage existing image models to make predictions on the extracted images.

As a first step of this workflow, the app extracts images (photo context) from point clouds and creates a new images project, which can then be used for further processing or analysis.

# How To Use

Simply run the app from the context menu of a project or dataset. The app will automatically extract all related images from the point clouds and create a new images project with the same dataset structure as the original project.

The output project will have:

- The same name as the input project with suffix "(Photo Context)"
- The same dataset structure as the input project
- All related images extracted from point clouds with preserved metadata and source point cloud IDs in the filenames. Image metadata will include the parent point cloud ID for reference (it will be used in the future to synchronize the images with the point cloud data).
