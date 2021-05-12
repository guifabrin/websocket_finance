import "../styles/index.sass";

import uniqueUsernameDirective from './directives/uniqueUsernameDirective'
import sameAsDirective from './directives/sameAsDirective'

import angular from 'angular'
import 'angular-messages'
import 'angular-material'
import mainCtrl from './controllers/mainCtrl';
import loginCtrl from './controllers/loginCtrl';
import registerCtrl from './controllers/registerCtrl';
import feedCtrl from './controllers/feedCtrl';

var app = angular.module('myApp', ['ngMaterial', 'ngMessages'], function ($interpolateProvider) {
    $interpolateProvider.startSymbol('<{');
    $interpolateProvider.endSymbol('}>');
});

app.controller('mainCtrl', mainCtrl);
app.controller('loginCtrl', loginCtrl);
app.controller('registerCtrl', registerCtrl);
app.controller('feedCtrl', feedCtrl);

app.directive('uniqueUsername', uniqueUsernameDirective);
app.directive('sameAs', sameAsDirective);