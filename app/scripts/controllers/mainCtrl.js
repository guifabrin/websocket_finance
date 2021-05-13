import URLHelper from '../helpers/URLHelper'

export default function ($scope, $mdDialog) {
    $scope.auth = localStorage.getItem('auth');
    $scope.message = URLHelper.getParam('message');
    $scope.pages = [
        { path: '/', name: 'Home' },
    ]
    if ($scope.auth) {
        [$scope.username] = atob($scope.auth).split(':');
        $scope.pages.push({ path: '/feed', name: 'Feed' })
        $scope.pages.push({ path: '/user', name: $scope.username })
    } else {
        $scope.pages.push({ path: '/register', name: 'Register' })
        $scope.pages.push({ path: '/login', name: 'Login' })
    }
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