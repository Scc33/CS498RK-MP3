var secrets = require('../config/secrets');
const user = require('../models/user');
const task = require('../models/task');
const { response } = require('express');
const { Error } = require('mongoose');

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
    taskRoute.get(async function (req, res) {
        try {
            var where = {};
            if (req.query.where) {
                where = JSON.parse(req.query.where);
                console.log(where);
            }
            /*for (const [key, value] of Object.entries(req.query)) {
                    console.log(key, value);
                    console.log(data.exec(key, value));
                  }*/
            var result = await task.find(where);
            if (result) {
                res.status(200).json({
                    "message": "Ok",
                    "data": result
                });
            } else {
                res.status(404).json({ 
                    "message": "Error no tasks found",
                    "data": result
                });
            }
        } catch (err) {
            res.status(500).send(err);
        }
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
    individualTaskRoute.get(async function (req, res) {
        try {
            let result = await task.findById({_id: req.params.id}).exec();
            if (result === null) {
                res.status(404).json({
                    "message": "Error that task cannot be found",
                    "data": err
                });
            } else {
                res.status(200).json({
                    "message": "Ok",
                    "data": result
                });
            }
        } catch (err) {
            res.status(404).json({
                "message": "Error that task cannot be found",
                "data": err
            });
        }
    });

    individualTaskRoute.delete(async function (req, res) {
        try {
            var result = await task.deleteOne({ _id: req.params.id }).exec();
            res.status(200).json({ 
                "message": "Ok",
                "data": result 
            })
        } catch (err) {
            res.status(404).json({
                "message": "Error that task cannot be found",
                "data": err
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
            res.status(201).json({ 
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

    var individualUserRoute = router.route('/users/:id')
    individualUserRoute.get(async function (req, res) {
        try {
            let result = await user.findById({_id: req.params.id}).exec();
            if (result === null) {
                res.status(404).json({
                    "message": "Error that user cannot be found",
                    "data": err
                });
            } else {
                res.status(200).json({
                    "message": "Ok",
                    "data": result
                });
            }
        } catch (err) {
            res.status(404).json({
                "message": "Error that user cannot be found",
                "data": err
            });
        }
    });

    individualUserRoute.put(async function (req, res) {
        try {
            let result = await user.findByIdAndUpdate({_id: req.params.id}, req.body, {new: true}).exec();
            res.status(200).json({
                "message": "Ok",
                "data": result
            });
        } catch (err) {
            res.status(404).json({
                "message": "Error that user cannot be found",
                "data": err
            });
        }
    });

    individualUserRoute.delete(async function (req, res) {
        try {
            var result = await user.deleteOne({ _id: req.params.id }).exec();
            res.status(200).json({ 
                "message": "Ok",
                "data": result 
            })
        } catch (err) {
            res.status(404).json({
                "message": "Error that user cannot be found",
                "data": err
            });
        }
    });

    return router;
}
