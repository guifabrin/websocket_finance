
export default function ($scope) {
    $scope.posts = [];
    $scope.update = () => {
        fetch('/api/v1/posts').then((response) => response.json()).then((arrPosts) => {
            $scope.posts = arrPosts;
            $scope.$apply();
        });
    }
    $scope.update();
}