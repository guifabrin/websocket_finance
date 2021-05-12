import URLHelper from '../helpers/URLHelper'

export default function ($scope, $mdDialog) {
    $scope.message = URLHelper.getParam('message');

    if ($scope.message) {
        $mdDialog.show(
            $mdDialog.alert()
                .clickOutsideToClose(true)
                .title('Message')
                .textContent(decodeURI($scope.message))
                .ok('Got it!')
        );
    }
};