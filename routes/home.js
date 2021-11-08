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

    async function get(req, res) {
        try {
            var where = {};
            if (req.query.where) {
                where = JSON.parse(req.query.where);
            }
            var select = {};
            if (req.query.select) {
                select = JSON.parse(req.query.select);
            }
            var sort = {};
            if (req.query.sort) {
                sort = JSON.parse(req.query.sort);
            }
            var result;
            if (req.route.path === '/users') {
                result = await user.find(where)
                    .select(select)
                    .sort(sort)
                    .skip(parseFloat(req.query.skip))
                    .limit(parseFloat(req.query.limit));
            } else if (req.route.path === '/tasks') {
                result = await task.find(where)
                    .select(select)
                    .sort(sort)
                    .skip(parseFloat(req.query.skip))
                    .limit(parseFloat(req.query.limit));
            }
            if (req.query.count === "true") {
                result = result.length;
            }
            if (result) {
                res.status(200).json({
                    "message": "Ok",
                    "data": result
                });
            } else {
                res.status(404).json({
                    "message": "Error the returned tasks don't exist",
                    "data": result
                });
            }
        } catch (err) {
            res.status(500).json({
                "message": "Error, that is something unknown",
                "data": err
            });
        }
    }

    /*
     * TASKS
     */

    var taskRoute = router.route('/tasks');
    taskRoute.get(get);

    taskRoute.post(async function (req, res) {
        if (req.body.name && req.body.deadline) {
            var t = new task(req.body);
            let result;
            
            try {
                result = await t.save();
                res.status(201).json({
                    "message": "Ok",
                    "data": result
                });
            } catch (err) {
                res.status(500).json({
                    "message": "Error, that is something unknown",
                    "data": err
                });
            }
        } else {
            res.status(400).json({
                "message": "Error, you need to provide a name and deadline",
                "data": req.body
            });
        }
    });

    var individualTaskRoute = router.route('/tasks/:id')
    individualTaskRoute.get(async function (req, res) {
        try {
            let result = await task.findById({ _id: req.params.id }).exec();
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

    individualTaskRoute.put(async function (req, res) {
        if (req.body.name && req.body.deadline) {
            try {
                let result = await user.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).exec();
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
        } else {
            res.status(400).json({
                "message": "Error, you need to provide a name and deadline",
                "data": ""
            });
        }
    });

    individualTaskRoute.delete(async function (req, res) {
        try {
            var result = await task.deleteOne({ _id: req.params.id }).exec();
            if (result.deletedCount === 0) {
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
            res.status(500).json({
                "message": "Something weird happened behind the scenes",
                "data": err
            });
        }
    });

    /*
     * USERS
     */

    var userRoute = router.route('/users');
    userRoute.get(get);

    userRoute.post(async function (req, res) {
        if (req.body.name && req.body.email) {
            var u = new user(req.body);
            let result;

            try {
                result = await u.save()
                res.status(201).json({
                    "message": "Ok",
                    "data": result
                })
            } catch (err) {
                res.json({
                    "message": "Error",
                    "data": err
                });
            }
        } else {
            res.status(400).json({
                "message": "Error, you need to provide a name and email",
                "data": ""
            });
        }
    });

    var individualUserRoute = router.route('/users/:id')
    individualUserRoute.get(async function (req, res) {
        try {
            let result = await user.findById({ _id: req.params.id }).exec();
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
            res.status(500).json({
                "message": "Error something strange happened behind the scenes",
                "data": err
            });
        }
    });

    individualUserRoute.put(async function (req, res) {
        if (req.body.name && req.body.email) {
            try {
                let result = await user.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).exec();
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
        } else {
            res.status(400).json({
                "message": "Error, you need to provide a name and email",
                "data": ""
            });
        }
    });

    individualUserRoute.delete(async function (req, res) {
        try {
            var result = await user.deleteOne({ _id: req.params.id }).exec();
            if (result.deletedCount === 0) {
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
            res.status(500).json({
                "message": "Error something strange happened behind the scenes",
                "data": err
            });
        }
    });

    return router;
}
