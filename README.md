# Project Management Application

A web application for handling co-operative projects.
[Available on fly.io](http://tsoha-project-management-app.fly.dev/)

## Functionality

### Implemented

- Users have a dashboard that acts as an overview of ongoing projects that they are a part of
- Creating new projects: Enter project name, description, deadline, members
- Project view
  - User can see details of the project
  - Creator of the project can edit the details, or remove the project
    - Other users can be given permissions for editing
  - Tasks can be added to projects
    - Tasks can be marked as: in progress, done
  - Projects are marked: not started, in progress, done, late
  - Project can be marked as done when all tasks are done

## Structure

- Tables:
  - Users: General details about the user (name, password) (x)
  - Projects: All the projects and their details (Name, description, deadline, status) (x)
  - ProjectUsers: Links user id to project id, and stores the user's permission mode (admin/member) (partial x)
  - ProjectTasks: Tasks assigned for projects are stored here (Name, deadline, status)
  - TasksUsers: maybe, for assigning users to tasks instead of tasks being general for all users
