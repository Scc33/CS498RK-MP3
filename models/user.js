// Load required packages
var mongoose = require('mongoose');

/*
Here is the User Schema:
"name" - String
"email" - String
"pendingTasks" - [String] - The _id fields of the pending tasks that this user has
"dateCreated" - Date - should be set automatically by server*/

// Define our user schema
var UserSchema = new mongoose.Schema({
    name: String,
    email: String,
    pendingTasks: [String],
    dateCreated: { type: Date, default: Date.now }
});

// Export the Mongoose model
module.exports = mongoose.model('User', UserSchema);
