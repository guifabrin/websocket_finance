export default function () {
    return {
        require: 'ngModel',
        link: function (scope, { }, attrs, control) {
            control.$validators.same_as = function (value) {
                const [ngModel, parameter] = attrs.sameAs.split('.')
                return (scope[ngModel][parameter] == value)
            };
        }
    };
}