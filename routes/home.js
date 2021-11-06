var secrets = require('../config/secrets');
const user = require('../models/user');
const task = require('../models/task');
const { response } = require('express');

module.exports = function (router) {
    var homeRoute = router.route('/');
    homeRoute.get(function (req, res) {
        var connectionString = secrets.token;
        res.json({ message: 'My connection string is ' + connectionString });
    });

    /*
     * TASKS
     */

    var taskRoute = router.route('/tasks');
    taskRoute.get(function (req, res) {
        task.find({})
            .then((data) => {
                res.json({
                    "message": "Ok",
                    "data": data
                });
            })
            .catch(err => {
                res.json({
                    "message": "error",
                    "data": ""
                });
            });
    });

    taskRoute.post(async function (req, res) {
        var t = new task(req.body);
        let result;

        try {
            result = await t.save()
            res.json({ 
                "message": "Ok",
                "data": result 
            })
        } catch (err) {
            const errors = err.errors;
            Object.keys(errors).forEach(key => console.log(errors[key].message));
            res.json({
                "message": "error",
                "data": ""
            });
        }
        console.log(result)
    });

    var individualTaskRoute = router.route('/tasks/:id')
    individualTaskRoute.get(function (req, res) {
        var person = task.findById(request.params.id)
            .then((data) => {
                res.json({
                    "message": "Ok",
                    "data": data
                })
            }).catch(err => {
                res.json({
                    "message": "error",
                    "data": ""
                });
            });
    });

    individualTaskRoute.delete(async function (req, res) {
        try {
            var result = await task.deleteOne({ _id: request.params.id }).exec();
            res.json({ 
                "message": "Ok",
                "data": result 
            })
        } catch (error) {
            response.status(500).send(error);
            res.json({
                "message": "error",
                "data": ""
            });
        }
    });


    /*
     * USERS
     */

    var userRoute = router.route('/users');
    userRoute.get(function (req, res) {
        user.find({})
            .then((data) => {
                res.status(200).json({
                    "message": "Ok",
                    "data": data
                })
            })
            .catch(err => {
                res.status(404).json({
                    "message": "That's an error. The users cannot be found",
                    "data": err
                });
            });
    });

    userRoute.post(async function (req, res) {
        var u = new user(req.body);
        let result;

        try {
            result = await u.save()
            res.json({ 
                "message": "Ok",
                "data": result 
            })
        } catch (err) {
            const errors = err.errors;
            Object.keys(errors).forEach(key => console.log(errors[key].message));
            res.json({
                "message": "error",
                "data": ""
            });
        }
        console.log(result)
    });

    var testRoute = router.route('/test');
    testRoute.get(function (req, res) {
        //res.json({ message: 'test' });

        const Data = {
            name: 'test',
            email: 'test@gmail.com',
            pendingTasks: []
        }
        console.log(Data);
        const testData = new user(Data)
        console.log(testData)
        testData.save((error) => {
            if (error) {
                console.log("darn");
                res.status(404);
            } else {
                console.log("saved!")
                res.status(201).json({ 
                    "message": "Ok",
                    "data": "ASDF" 
                })
            }
        });
    });

    return router;
}
