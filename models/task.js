// Load required packages
var mongoose = require('mongoose');

/*
Here is the Task Schema:

"name" - String
"description" - String
"deadline" - Date
"completed" - Boolean
"assignedUser" - String - The _id field of the user this task is assigned to - default ""
"assignedUserName" - String - The name field of the user this task is assigned to - default "unassigned"
"dateCreated" - Date - should be set automatically by server to present date*/

// Define our user schema
var TaskSchema = new mongoose.Schema({
    name: String,
    description: String,
    deadline: Date,
    completed: Boolean,
    assignedUser: String,
    assignedUserName: String,
    dateCreated: {type: Date, default: Date.now}
});

// Export the Mongoose model
module.exports = mongoose.model('Task', TaskSchema);
