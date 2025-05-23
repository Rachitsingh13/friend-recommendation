$(document).ready(function() {
    const userSelect = $('#userSelect');
    const userInfo = $('#userInfo');
    const friendsList = $('#friendsList');
    const recommendationsList = $('#recommendationsList');

    function showLoading(element) {
        element.html('<div class="text-center"><div class="spinner-border text-primary" role="status"></div></div>');
    }

    function showError(element, message) {
        element.html(`<div class="alert alert-danger" role="alert">${message}</div>`);
    }

    userSelect.change(function() {
        const userId = $(this).val();
        if (userId) {
            userInfo.removeClass('d-none');
            loadFriendsAndRecommendations(userId);
        } else {
            userInfo.addClass('d-none');
            friendsList.empty();
            recommendationsList.empty();
        }
    });

    function loadFriendsAndRecommendations(userId) {
        showLoading(friendsList);
        $.get(`/api/friends/${userId}`, function(friends) {
            friendsList.empty();
            if (friends.length > 0) {
                friends.forEach((friend, index) => {
                    friendsList.append(`
                        <li class="list-group-item" style="animation-delay: ${index * 100}ms">
                            <i class="fas fa-user-circle"></i>
                            ${friend}
                        </li>
                    `);
                });
            } else {
                friendsList.html('<div class="alert alert-info">No friends found</div>');
            }
        }).fail(function() {
            showError(friendsList, 'Error loading friends');
        });

        showLoading(recommendationsList);
        $.get(`/api/recommendations/${userId}`, function(recommendations) {
            recommendationsList.empty();
            if (recommendations.length > 0) {
                recommendations.forEach((rec, index) => {
                    recommendationsList.append(`
                        <li class="list-group-item d-flex justify-content-between align-items-center" 
                            style="animation-delay: ${index * 100}ms">
                            <div>
                                <i class="fas fa-user-plus"></i>
                                ${rec.name}
                            </div>
                            <span class="common-friends-badge">
                                ${rec.common_friends} mutual friend${rec.common_friends !== 1 ? 's' : ''}
                            </span>
                        </li>
                    `);
                });
            } else {
                recommendationsList.html('<div class="alert alert-info">No recommendations found</div>');
            }
        }).fail(function() {
            showError(recommendationsList, 'Error loading recommendations');
        });
    }
}); 