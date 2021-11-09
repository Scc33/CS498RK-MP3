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
            // TODO need to update the associated user if exists

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
        // TODO need to update the associated user if exists?
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
            const t = await task.findOne({ _id: req.params.id });
            if (t) {
                var userToUpdate = t.assignedUser;
                var u = null;
                if (userToUpdate) {
                    u = await user.findOne({ _id: userToUpdate });
                }
                if (u) {
                    var arr = u.pendingTasks;
                    var index = arr.indexOf(req.params.id);
                    if (index > -1) {
                        arr.splice(index, 1);
                    }
                    u.pendingTasks = arr;
                    var updateTask = await u.save();
                    if (updateTask === null) {
                        res.status(500).json({
                            "message": "Error something strange happened behind the scenes",
                            "data": err
                        });
                    }
                }

                var result = await task.deleteOne({ _id: req.params.id });
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
            } else {
                res.status(404).json({
                    "message": "Error that task cannot be found",
                    "data": err
                }).send();
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
        // TODO need to update the associated task if exists
        if (req.body.name && req.body.email) {
            var searchEmail = await user.find({ "email": req.body.email });
            if (searchEmail.length !== 0) {
                res.status(400).json({
                    "message": "Error, that email is already in use",
                    "data": searchEmail
                });
            } else {
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
        // TODO need to update the associated user if exists?
        if (req.body.name && req.body.email) {
            var searchEmail = await user.find({ "email": req.body.email });
            if (searchEmail.length !== 0 && JSON.stringify(searchEmail[0]._id) !== JSON.stringify(req.params.id)) {
                res.status(400).json({
                    "message": "Error, that email is already in use",
                    "data": searchEmail
                });
            } else {
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
            var u = await user.find({ _id: req.params.id });
            var tasks = u[0].pendingTasks;
            for (var i = 0; i < tasks.length; i++) {
                var t = await task.findOne({ _id: tasks[i] });
                if (t) {
                    t.assignedUser = "";
                    t.assignedUserName = "unassigned"
                    var updateTask = await t.save();
                    if (updateTask === null) {
                        res.status(500).json({
                            "message": "Error something strange happened behind the scenes",
                            "data": err
                        });
                    }
                }
            }
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
