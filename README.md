
# Project Management Application

A web application for handling co-operative projects.    
Note for reviews: everything in the project will be written in English, but feedback may be given in either Finnish or English!

### Functionality

- Users have a dashboard that acts as an overview of ongoing projects that they are a part of
	- Tasks are marked: not started, in progress, done, (late)
- Creating new projects:
	- Enter project name, description, tasks, (deadline(s)), members
- Project view
	- User can see details of the project
	- Tasks can be marked as: not started, in progress, done
	- Project is marked as done when all tasks are done
	- Creator of the project can edit the details, or remove the project
		- Maybe: Other users can be given permissions for editing
	- Maybe: Projects have internal messaging (will implement if there is sufficient time)
	
### Structure
- Tables:
	- Users: General details about the user (name, admin)
	- UserDetails: Password stuff so secure stuff. Don't know how this is implemented yet, will leave further details for later
	- Projects: All the projects and their details (Name, description, deadline)
	- ProjectUsers: Links user id to project id, and stores the user's permission mode (admin/member)
	- ProjectTasks: Tasks assigned for projects are stored here (Name, deadline, status)
	- (TasksUsers: maybe, for assigning users to tasks instead of tasks being general for all users. Will consider this)
	- (Messages: maybe, will need other tables too which can be a lot of work. As mentioned before, will leave this for later if there is time)
