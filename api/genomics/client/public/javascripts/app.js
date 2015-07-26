angular.module('genomicsDemo', [])

.controller('mainController', function($scope, $http) {
  
  // Get count
  $http({
    url : '/api/count/',
    method : "GET",
    params : {}
  })
  .success(function(data) {
    $scope.gpCount = data[0].count;
    console.log(data);
  })
  .error(function(error) {
    console.log('Error: ' + error);
  });

  // Search by gene entity
  $scope.searchByGene = function() {
    if ($scope.formData.geneId) {
      console.log($scope.formData);
      $http({
        url : '/api/gp/',
        method : "GET",
        params : $scope.formData
      })
      .success(function(data) {
        $scope.gpResults = data;
        console.log(data);
      })
      .error(function(error) {
        console.log('Error: ' + error);
      });
    }
  }
});
