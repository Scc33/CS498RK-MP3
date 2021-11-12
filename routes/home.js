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
                //console.log(req.body, req.body.assignedUser);
                if (req.body.assignedUser) {
                    var u = await user.findOne({ _id: req.body.assignedUser });
                    //console.log(u, req.body.assignedUser);
                    if (u) {
                        result = await t.save();
                        if (u.pendingTasks.indexOf(result._id) === -1) {
                            console.log("post", u.pendingTasks, result._id);
                            u.pendingTasks.push(result._id);
                            console.log("post", u.pendingTasks, result._id);
                            var savedUser = await u.save();
                        }
                        res.status(201).json({
                            "message": "Ok",
                            "data": result
                        });
                    } else {
                        req.body.assignedUserName = "unassigned";
                        req.body.assignedUser = "";
                        t = new task(req.body);
                        result = await t.save();
                        res.status(201).json({
                            "message": "Task created but with no assigned user",
                            "data": result
                        });
                    }
                } else {
                    result = await t.save();
                    res.status(201).json({
                        "message": "Ok",
                        "data": result
                    });
                }
            } catch (err) {
                console.log(err)
                res.status(500).json({
                    "message": "Error, that is something unknown",
                    "data": err
                });
            }
        } else {
            console.log(req.body);
            res.status(400).json({
                "message": "Missing fields, need name and deadline to post a task",
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
                    "data": ""
                });
            } else {
                res.status(200).json({
                    "message": "Ok",
                    "data": result
                });
            }
        } catch (err) {
            res.status(500).json({
                "message": "Error some backend issue",
                "data": err
            });
        }
    });

    individualTaskRoute.put(async function (req, res) {
        if (req.body.name && req.body.deadline) {
            try {
                var u = await user.findOne({ _id: req.body.assignedUser });
                if (u && u.name == req.body.assignedUserName) {
                    var result = await task.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).exec();
                    if (result) {
                        if (u.pendingTasks.indexOf(result._id) === -1) {
                            console.log("put", u.pendingTasks, result._id);
                            u.pendingTasks.push(result._id);
                            console.log("put", u.pendingTasks, result._id);
                            var savedUser = await user.findByIdAndUpdate({ _id: req.body.assignedUser }, u, { new: true }).exec();
                        }
                        if (req.body.completed) {
                            var arr = u.pendingTasks;
                            var index = arr.indexOf(req.params.id);
                            if (index > -1) {
                                arr.splice(index, 1);
                            }
                            u.pendingTasks = arr;
                            var savedUser = await user.findByIdAndUpdate({ _id: req.body.assignedUser }, u, { new: true }).exec();
                        }
                        res.status(200).json({
                            "message": "Ok",
                            "data": result
                        });
                    } else {
                        res.status(404).json({
                            "message": "Error that task cannot be found",
                            "data": ""
                        });
                    }
                } else {
                    req.body.assignedUserName = "unassigned";
                    req.body.assignedUser = "";
                    t = new task(req.body);
                    result = await t.save();
                    res.status(200).json({
                        "message": "Task updated but with no assigned user",
                        "data": result
                    });
                }
            } catch (err) {
                console.log("put", err)
                res.status(500).json({
                    "message": "Error, that is something unknown",
                    "data": err
                });
            }
        } else {
            res.status(400).json({
                "message": "Missing fields, need name and deadline to put a task",
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
                    if (updateTask == null) {
                        res.status(500).json({
                            "message": "Error something strange happened behind the scenes",
                            "data": ""
                        });
                    }
                }

                var result = await task.deleteOne({ _id: req.params.id });
                if (result.deletedCount === 0) {
                    res.status(404).json({
                        "message": "Error that task cannot be found",
                        "data": ""
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
                    "data": ""
                }).send();
            }
        } catch (err) {
            console.log(err)
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
        console.log("userpost", req.body, req.params);
        if (req.body.name && req.body.email) {
            var searchEmail = await user.find({ "email": req.body.email });
            if (searchEmail.length !== 0) {
                res.status(400).json({
                    "message": "Error, that email is already in use",
                    "data": searchEmail
                });
            } else {
                console.log("userPost", typeof (req.body.pendingTasks), req.body.pendingTasks)
                var u = new user(req.body);
                let result;

                try {
                    result = await u.save()
                } catch (err) {
                    console.log(err)
                    res.status(500).json({
                        "message": "Error, something bad happened",
                        "data": err
                    });
                }

                if (u.pendingTasks) {
                    if (Array.isArray(req.body.pendingTasks)) {
                        for (var i = 0; i < req.body.pendingTasks.length; i++) {
                            var t = await task.findOne({ _id: req.body.pendingTasks[i] });
                            if (t) {
                                if (t.completed) {
                                    var arr = req.body.pendingTasks;
                                    var index = arr.indexOf(req.body.pendingTasks[i]);
                                    if (index > -1) {
                                        arr.splice(index, 1);
                                    }
                                    req.body.pendingTasks = arr;
                                } else {
                                    t.assignedUser = req.body._id;
                                    t.assignedUserName = req.body.name;
                                    var updatedTask = await task.findByIdAndUpdate({ _id: t._id }, t, { new: true }).exec();
                                }
                            } else {
                                var arr = req.body.pendingTasks;
                                var index = arr.indexOf(req.body.pendingTasks[i]);
                                if (index > -1) {
                                    arr.splice(index, 1);
                                }
                                req.body.pendingTasks = arr;
                            }
                        }
                    } else {
                        console.log("userPostPending", req.body.pendingTasks)
                        var t = await task.findOne({ _id: req.body.pendingTasks });
                        console.log(t);
                        if (t) {
                            if (t.completed) {
                                req.body.pendingTasks = [];
                            } else {
                                console.log("not completed", t, t.completed)
                                t.assignedUser = req.body._id;
                                t.assignedUserName = req.body.name;
                                console.log("not completed", t, t.completed)
                                var updatedTask = await task.findByIdAndUpdate({ _id: t._id }, t, { new: true }).exec();
                                //console.log(updatedTask._id);
                            }
                        } else {
                            req.body.pendingTasks = [];
                        }
                    }

                    try {
                        result = await user.findByIdAndUpdate({ _id: u._id }, req.body, { new: true }).exec();
                        res.status(201).json({
                            "message": "Ok",
                            "data": result
                        })
                    } catch (err) {
                        console.log(err)
                        res.status(500).json({
                            "message": "Error, something bad happened",
                            "data": err
                        });
                    }
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
                    "data": ""
                });
            } else {
                res.status(200).json({
                    "message": "Ok",
                    "data": result
                });
            }
        } catch (err) {
            console.log(err)
            res.status(500).json({
                "message": "Error something strange happened behind the scenes",
                "data": err
            });
        }
    });

    individualUserRoute.put(async function (req, res) {
        console.log("userput", req.body, req.params);
        if (req.body.name && req.body.email) {
            var searchEmail = await user.find({ "email": req.body.email });
            if (searchEmail.length !== 0 && JSON.stringify(searchEmail[0]._id) !== JSON.stringify(req.params.id)) {
                res.status(400).json({
                    "message": "Error, that email is already in use",
                    "data": searchEmail
                });
            } else {
                try {
                    var oldUser = await user.findById({ _id: req.params.id });
                    if (oldUser) {
                        if (!req.body.pendingTasks) {
                            req.body.pendingTasks = oldUser.pendingTasks;
                            console.log(req.body.pendingTasks)
                            if (!req.body.pendingTasks) {
                                req.body.pendingTasks = [];
                            }
                        }
                        console.log("no new tasks given so finding old", req.body.pendingTasks)
                        var t = await task.find({ assignedUser: req.params.id });
                        console.log(t, req.body.pendingTasks);
                        if (t && req.body.pendingTasks) {
                            for (let i = 0; i < t.length; i++) {
                                if (t[i].completed) {
                                    if (Array.isArray(req.body.pendingTasks)) {
                                        var arr = req.body.pendingTasks;
                                        var index = arr.indexOf(req.body.pendingTasks[i]);
                                        if (index > -1) {
                                            arr.splice(index, 1);
                                        }
                                        req.body.pendingTasks = arr;
                                    } else {
                                        req.body.pendingTasks = [];
                                    }
                                }
                                console.log(t[i])
                                t[i].assignedUser = req.params.id;
                                t[i].assignedUserName = req.body.name;
                                console.log(t[i])
                                console.log(t[i]._id)
                                const taskUpdated = task.findByIdAndUpdate({ _id: t[i]._id }, { $set: t[i] }, { new: true }).exec();
                            }
                        }
    
                        let result = await user.findByIdAndUpdate({ _id: req.params.id }, { $set: req.body }, { new: true }).exec();
                        if (result) {
                            res.status(200).json({
                                "message": "Ok",
                                "data": result
                            });
                        } else {
                            res.status(404).json({
                                "message": "Error that user cannot be found",
                                "data": ""
                            });
                        }
                    } else {
                        res.status(404).json({
                            "message": "Error that user cannot be found",
                            "data": ""
                        });
                    }
                } catch (err) {
                    console.log(err)
                    res.status(500).json({
                        "message": "Error something strange happened behind the scenes",
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
            var u = await user.findOne({ _id: req.params.id });
            if (u) {
                var tasks = u.pendingTasks;
                for (var i = 0; i < tasks.length; i++) {
                    var t = await task.findOne({ _id: tasks[i] });
                    if (t) {
                        t.assignedUser = "";
                        t.assignedUserName = "unassigned"
                        var updateTask = await t.save();
                        if (updateTask === null) {
                            res.status(500).json({
                                "message": "Error something strange happened behind the scenes",
                                "data": ""
                            });
                        }
                    }
                }
                var result = await user.deleteOne({ _id: req.params.id }).exec();
                if (result.deletedCount === 0) {
                    res.status(404).json({
                        "message": "Error that user cannot be found",
                        "data": ""
                    });
                } else {
                    res.status(200).json({
                        "message": "Ok",
                        "data": result
                    });
                }
            } else {
                res.status(404).json({
                    "message": "Error that user cannot be found",
                    "data": ""
                });
            }
            
        } catch (err) {
            console.log(err)
            res.status(500).json({
                "message": "Error something strange happened behind the scenes",
                "data": err
            });
        }
    });

    return router;
}
