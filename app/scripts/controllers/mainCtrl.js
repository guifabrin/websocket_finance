import URLHelper from '../helpers/URLHelper'

export default function ($scope, $mdDialog) {
    $scope.message = URLHelper.getParam('message');
    $scope.pages = [
        { path: '/', name: 'Home' },
        { path: '/register', name: 'Register' },
        { path: '/login', name: 'Login' },
        { path: '/feed', name: 'Feed' },
    ]
    $scope.currentPage = window.location.pathname;
    $scope.goto = (path) => {
        window.location.href = path;
    }
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