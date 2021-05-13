import URLHelper from '../helpers/URLHelper'

export default function ($scope, $mdDialog) {
    try {
        $scope.auth = localStorage.getItem('auth');
        $scope.message = URLHelper.getParam('message');
        if ($scope.auth)
            [$scope.username] = atob($scope.auth).split(':');
    } catch (e) {
        $scope.username = '';
    }
    $scope.pages = [
        { path: '/', name: 'Home' },
    ]
    if ($scope.username) {
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