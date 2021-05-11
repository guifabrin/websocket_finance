import "../styles/index.sass";

import uniqueUsernameDirective from './directives/uniqueUsernameDirective'
import sameAsDirective from './directives/sameAsDirective'

import angular from 'angular'
import 'angular-messages'
import 'angular-material'

var app = angular.module('myApp', ['ngMaterial', 'ngMessages'], function ($interpolateProvider) {
    $interpolateProvider.startSymbol('<{');
    $interpolateProvider.endSymbol('}>');
});

app.controller('mainCtrl', require('./controllers/mainCtrl'));
app.controller('registerCtrl', require('./controllers/registerCtrl'));

app.directive('uniqueUsername', uniqueUsernameDirective);
app.directive('sameAs', sameAsDirective);