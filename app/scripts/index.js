var angular = require('angular')

var app = angular.module('myApp', [], function ($interpolateProvider) {
    $interpolateProvider.startSymbol('<{');
    $interpolateProvider.endSymbol('}>');
});

app.controller('mainCtrl', require('./controllers/mainCtrl'));