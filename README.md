![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/9cb9051d-24e7-4361-b93f-e2efa5eb4290)# Rio Tinto FrontRunner Optimization Project

## Overview

This project focuses on optimizing the use of Rio Tinto's FrontRunner software for autonomous haul trucks. The primary goal is to enhance the efficiency of road curve drawing at intersections, particularly T-intersections, to reduce truck cycle time, increase productivity, and lower operational costs. The project involves developing a model to classify road curves, an optimizer to generate the best road curves, and a front-end application to integrate with the FrontRunner system.

## Table of Contents

- [Project Description](#project-description)
  - [Role of Haul Trucks](#role-of-haul-trucks)
  - [Use of FrontRunner Software](#use-of-frontrunner-software)
  - [Difficulties with FrontRunner](#difficulties-with-frontrunner)
  - [Impact on Iron Mining Operations](#impact-on-iron-mining-operations)
- [Objectives and Tasks](#objectives-and-tasks)
- [Solution Approach](#solution-approach)
  - [Model Development](#model-development)
  - [Optimizer Development](#optimizer-development)
  - [Technology Integration](#technology-integration)
- [Data Analysis](#data-analysis)
  - [Parameters and Constraints](#parameters-and-constraints)
  - [Parameter Weight Analysis](#parameter-weight-analysis)
- [Optimization Model](#optimization-model)
- [Frontend Development](#frontend-development)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Description

### Role of Haul Trucks

Rio Tinto uses the FrontRunner software to manage autonomous haul truck fleets that transport iron ore through a complex network of roads from pits to the ore processing plant.
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/d7fe6496-61b7-4240-9ab6-58422e27400d)


### Use of FrontRunner Software

FrontRunner enables remote pit controllers to manually draw the mine site road networks that the haul trucks travel.
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/44a56885-0e63-4313-995f-7d2deb5db5ab)

### Difficulties with FrontRunner

Drawing road curves, especially through T-intersections, is time-consuming for controllers. Poorly drawn road curves can increase truck cycle time, reduce truck productivity, and increase operational costs.
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/bdc122f8-0a2e-46bc-addf-fc15f000c5e4)


### Impact on Iron Mining Operations

Inefficiencies in road curve drawing can lead to significant reductions in throughput, increased fuel costs, and higher maintenance costs, potentially resulting in millions of dollars in losses annually.


## Objectives and Tasks

The hackathon focuses on three main tasks:

1. **Build the Model**: Develop a model to determine what constitutes a good or bad curve based on the provided dataset.
2. **Build the Optimizer**: Use data modeling techniques to optimize road curve generation at intersections, thereby reducing cycle time.
3. **Build the Tech**: Create an application/system that integrates with Rio Tinto's FrontRunner system.

## Solution Approach

### Model Development

Develop a model to classify good and bad road curves using a loss function model that considers the following parameters:
- Path length
- Time to traverse the intersection
- Curvature radius
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/e12eb85c-4884-43ef-ba2d-ba93c05ce389)


### Optimizer Development

Create an optimizer model using a differential evolution algorithm to generate the best road curves at intersections while adhering to defined constraints:
- Road curves must remain within intersection boundaries.
- Curves must be a certain distance from intersection edges and adjacent curves.
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/b48736c3-8ce0-43a0-bec7-49fb7179b105)


### Technology Integration

Develop a front-end application using HTML and JavaScript to visualize and integrate the optimized road curves with the FrontRunner system.

## Data Analysis

### Parameters and Constraints

Define parameter ranges and constraints based on historical data analysis:
- Path Length: (111.65 meters, 407.63 meters)
- Time Difference: (21.45 seconds, 90.17 seconds)
- Curvature Radius: (0 meters, 196.45 meters)
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/4de62153-0291-4ee6-8196-1f4113492014)
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/27af1e04-807d-4438-91f6-3d5e0d1c3a16)


### Parameter Weight Analysis

Assign weights to parameters based on their impact on efficiency and safety:
- Transport Efficiency Priority: Path Length (0.4), Time Difference (0.4), Curvature Radius (0.2)
- Vehicle Stability Priority: Path Length (0.3), Time Difference (0.3), Curvature Radius (0.4)
- Balanced Consideration: Path Length (0.33), Time Difference (0.33), Curvature Radius (0.34)
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/df923bc7-17d5-4496-a766-99a8a4c204ca)

## Optimization Model

The optimization model uses a differential evolution algorithm to find the optimal road curve within the defined constraints. The model evaluates the quality of each path based on a weighted loss function and iteratively improves the path to minimize the loss.
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/ab5db75a-a53a-4d25-ba32-d81eb9125333)

## Frontend Development

Develop a front-end application to display the optimized road curves and facilitate integration with the FrontRunner system. The application includes:
- A user interface for controllers to view and adjust road curves
- Visualization tools to show the impact of the optimized curves
![image](https://github.com/HaitianWang/UWAYE-Hackathon-2024--RioTinto_BCG/assets/48538377/e43813a1-e283-4242-8e1c-e3a8c22715bc)


## Usage

1. Open the application in your web browser.
2. Upload the dataset files (Intersections.csv and Truck_Movements.csv).
3. View the optimized road curves and adjust as needed using the provided interface.
4. Save and export the optimized curves for integration with the FrontRunner system.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
