# Project Management Application

A web application for handling co-operative projects.
[Available on fly.io](https://tsoha-project-management-app.fly.dev/)

(Functionality marked with (x) has been implemented)

### Functionality

- Users have a dashboard that acts as an overview of ongoing projects that they are a part of (x)
  - Tasks are marked: not started, in progress, done, (late)
- Creating new projects: (x)
  - Enter project name, description, deadline(s), members (x)
- Project view
  - User can see details of the project (x)
  - Tasks can be marked as: not started, in progress, done
  - Project is marked as done when all tasks are done
  - Creator of the project can edit the details, or remove the project (partial x)
    - Maybe: Other users can be given permissions for editing
  - Maybe: Projects have internal messaging (will implement if there is sufficient time)

### Structure

- Tables:
  - Users: General details about the user (name, password) (x)
  - Projects: All the projects and their details (Name, description, deadline, status) (x)
  - ProjectUsers: Links user id to project id, and stores the user's permission mode (admin/member) (partial x)
  - ProjectTasks: Tasks assigned for projects are stored here (Name, deadline, status)
  - (TasksUsers: maybe, for assigning users to tasks instead of tasks being general for all users. Will consider this)
  - (Messages: maybe, will need other tables too which can be a lot of work. As mentioned before, will leave this for later if there is time)
