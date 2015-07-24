angular.module('genomicsDemo', [])

.controller('mainController', function($scope, $http) {

  $http.get('/api/gp/ENSG00000101255')
    .success(function(data) {
      $scope.gpResults = data;
      console.log(data);
    })
    .error(function(error) {
      console.log('Error: ' + error);
    });
  
  // Search by gene entity
  $scope.searchByGene = function() {
    if ($scope.formData.text) {
      $http.get('/api/gp/' + $scope.formData.text)
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
