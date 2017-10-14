var app = angular.module('myApp', ['ngRoute', 'ngAnimate', 'ngAria', 'ngMaterial']);
app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when("/", {
            templateUrl: "/views/home.html",
            controller: "mainPageCtrl"
        });
}]);

app.controller('mainPageCtrl', ['$scope', '$http', '$location', '$mdDialog', '$window', function($scope, $http, $location, $mdDialog, $window) {
    $scope.templates = [{
            name: 'Current Products',
            url: '/views/partials/currentProducts.html'
        },
        {
            name: 'Find Items',
            url: '/views/partials/findItems.html'
        }
    ];
    $scope.template = $scope.templates[0];

    $scope.changeToCurrentProducts = function() {
        $scope.template = $scope.templates[0];
    };

    $scope.changeToFindItems = function() {
        $scope.template = $scope.templates[1];
    };
    
    $scope.sortProductType = 'title';
    $scope.sortProductReverse = true;
    
    

    $scope.getCurrentProducts = function() {
        $http.get("/getCurrentProducts")
            .then(function(response) {
                $scope.currentProducts = response.data.sort(function(x, y) {
                    return ((x.title == y.title) ? 0 : ((x.title > y.title) ? 1 : -1 ));
                });
                console.log($scope.currentProducts);
                $scope.editButton = [];
                for (var i = 0; i < $scope.currentProducts.length; i++) {
                    $scope.editButton.push({
                        "editButtonClicked": "false"
                    });
                }
                
            });
    };
    $scope.getCurrentProducts();
    $scope.formData = {};

    $scope.editPriceToggle = function(index) {
        if (!$scope.editButton[index].editButtonClicked) {
            $scope.currentProducts[index].maxPrice = $scope.formData.maxPrice;
            $http.post("/saveCurrentProducts", JSON.stringify($scope.currentProducts))
                .then(function(response) {
                    console.log("Success");
                    $scope.formData.maxPrice = "";
                });
        }
        $scope.editButton[index].editButtonClicked = !$scope.editButton[index].editButtonClicked;

    };

    $scope.deleteItem = function(item) {
        $scope.currentProducts.splice($scope.currentProducts.indexOf(item), 1);
        $http.post("/saveCurrentProducts", JSON.stringify($scope.currentProducts))
            .then(function(response) {
                console.log($scope.currentProducts);
            });
    };
    
    $scope.addNewItem = function(ev) {
        $mdDialog.show({
            controller: DialogController,
            templateUrl: '/views/partials/dialog1.tmpl.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            clickOutsideToClose:true,
            fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
    })
    .then(function(answer) {
        var item = {
            "title" : answer.title,
            "upc" : answer.upc,
            "maxPrice" : answer.price
        };
        
        $scope.currentProducts.push(item);
        $scope.editButton.push({
            "editButtonClicked": "false"
        });
        $http.post("/saveCurrentProducts", JSON.stringify($scope.currentProducts))
            .then(function(response) {
                console.log("Success");
        });
        
        
    }, function() {
      console.log("Cancelled");
    });
  };

    $scope.titleSort = function(page) {
        if(page === "item") {
            $scope.sortItemReverse = !$scope.sortItemReverse;
            if(!$scope.sortItemReverse) {
                $scope.itemResults.sort(function(x, y) {
                     ((x.title == y.title) ? 0 : ((x.title > y.title) ? 1 : -1 ));
                });
            }
            else {
                $scope.itemResults.sort(function(x, y) {
                    return ((x.title == y.title) ? 0 : ((y.title > x.title) ? 1 : -1 ));
                });
            }
        }
        else {
            $scope.sortProductReverse = !$scope.sortProductReverse;
            if(!$scope.sortProductReverse) {
                $scope.currentProducts.sort(function(x, y) {
                    return ((x.title == y.title) ? 0 : ((x.title > y.title) ? 1 : -1 ));
                });
            }
            else {
                $scope.currentProducts.sort(function(x, y) {
                    return ((x.title == y.title) ? 0 : ((y.title > x.title) ? 1 : -1 ));
                });
            }
        }
        
    };

    $scope.priceSort = function(page) {
        if(page === "item") {
            $scope.sortItemReverse = !$scope.sortItemReverse;
            if(!$scope.sortItemReverse) {
                $scope.itemResults.sort(function(a, b) {
                    return a.price - b.price;
                });
            }
            else {
                $scope.itemResults.sort(function(a, b) {
                    return b.price - a.price;
                });
            }
        }
        else {
            $scope.sortProductReverse = !$scope.sortProductReverse;
            if(!$scope.sortProductReverse) {
                $scope.currentProducts.sort(function(a, b) {
                    return a.price - b.price;
                });
            }
            else {
                $scope.currentProducts.sort(function(a, b) {
                    return b.price - a.price;
                });
            }
        }
        

    };

    $scope.listingSort = function() {
        $scope.sortItemReverse = !$scope.sortItemReverse;
        if(!$scope.sortItemReverse) {
            $scope.itemResults.sort(function(x, y) {
                return ((x.listingType == y.listingType) ? 0 : ((x.listingType > y.listingType) ? 1 : -1 ));
            });
        }
        else {
            $scope.itemResults.sort(function(x, y) {
                return ((x.listingType == y.listingType) ? 0 : ((y.listingType > x.listingType) ? 1 : -1 ));
            });
        }
    };

    $scope.noItemsFound = false;
    $scope.itemsReturned = false;
    $scope.sortItemType = 'title';
    $scope.sortItemReverse = true;

    $scope.findItems = function() {
        $http.get("/findItems")
            .then(function(response) {
                if (response.data === "NoResults") {
                    $scope.noItemsFound = true;
                    $scope.itemsReturned = false;
                } else {
                    $scope.itemsReturned = true;
                    $scope.noItemsFound = false;
                    $scope.itemResults = response.data;
                    $scope.itemResults = response.data.sort(function(x, y) {
                        return ((x.title == y.title) ? 0 : ((x.title > y.title) ? 1 : -1 ));
                    });
                    console.log($scope.itemResults);
                }
            });
    };

    $scope.openItem = function(index) {
        $window.open($scope.itemResults[index].link, '_blank');
    };
    
    
    function DialogController($scope, $mdDialog) {
        $scope.hide = function() {
            $mdDialog.hide();
        };

        $scope.cancel = function() {
            $mdDialog.cancel();
        };

        $scope.answer = function(answer) {
            $mdDialog.hide(answer);
        };
    }

}]);