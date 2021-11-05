var secrets = require('../config/secrets');
const user = require('../models/user');

module.exports = function (router) {

    var homeRoute = router.route('/');
    homeRoute.get(function (req, res) {
        var connectionString = secrets.token;
        res.json({ message: 'My connection string is ' + connectionString });
    });

    var taskRoute = router.route('/tasks');
    taskRoute.get(function (req, res) {
        task.find({})
            .then((data) => {
                res.json({ "Tasks: ": data });
            })
            .catch(err => {
                res.status(404).send("Error: " + err);
            });
    });

    taskRoute.post(function (req, res) {
        var task = new task(req.body);
        task.save((error) => {
            if (error) {
                console.log("darn");
            } else {
                console.log("saved!")
            }
        });
    });

    var userRoute = router.route('/users');
    userRoute.get(function (req, res) {
        user.find({})
            .then((data) => {
                res.json({ "Users: ": data });
            })
            .catch(err => {
                res.status(404).send("Error: " + err);
            });
    });

    userRoute.post(function (req, res) {
        var task = new task(req.body);
        user.save((error) => {
            if (error) {
                console.log("darn");
            } else {
                console.log("saved!")
            }
        });
    });

    var testRoute = router.route('/test');
    testRoute.get(function (req, res) {
        res.json({ message: 'test' });

        const Data = {
            name: 'test',
            email: 'test@gmail.com',
            pendingTasks: []
        }
        const testData = new user(Data)
        testData.save((error) => {
            if (error) {
                console.log("darn");
            } else {
                console.log("saved!")
            }
        });
    });

    return router;
}
