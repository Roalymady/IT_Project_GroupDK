document.addEventListener("DOMContentLoaded", function () {
    initAutoDismissAlerts();
    initCategoryFilters();
    initAddItemForm();
    initDeadlineCountdown();
    initCreateGroupBuyForm();
});

// Automatically dismiss Django messages after a short delay
function initAutoDismissAlerts() {
    var alertNodes = document.querySelectorAll('.alert[data-auto-dismiss="true"]');
    if (!alertNodes.length) {
        return;
    }

    alertNodes.forEach(function (alertNode) {
        var delayAttribute = alertNode.getAttribute("data-auto-dismiss-delay");
        var delay = parseInt(delayAttribute || "5000", 10);

        if (Number.isNaN(delay) || delay < 0) {
            delay = 5000;
        }

        window.setTimeout(function () {
            if (typeof bootstrap === "undefined" || !bootstrap.Alert) {
                alertNode.classList.remove("show");
                alertNode.classList.add("fade");
                alertNode.addEventListener("transitionend", function () {
                    alertNode.remove();
                });
                return;
            }

            var alertInstance = bootstrap.Alert.getOrCreateInstance(alertNode);
            alertInstance.close();
        }, delay);
    });
}

// Filter group buy cards on the dashboard without reloading the page
function initCategoryFilters() {
    var filterButtons = document.querySelectorAll(".js-category-filter");
    var groupbuyColumns = document.querySelectorAll(".js-groupbuy-list [data-category]");

    if (!filterButtons.length || !groupbuyColumns.length) {
        return;
    }

    filterButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            var selectedFilter = button.getAttribute("data-filter");

            filterButtons.forEach(function (otherButton) {
                otherButton.classList.remove("active");
                otherButton.setAttribute("aria-pressed", "false");
            });

            button.classList.add("active");
            button.setAttribute("aria-pressed", "true");

            groupbuyColumns.forEach(function (column) {
                var category = column.getAttribute("data-category");
                var shouldShow = selectedFilter === "all" || category === selectedFilter;

                column.style.display = shouldShow ? "" : "none";
            });
        });
    });
}

// Handle adding new items on the detail page without reloading the page
function initAddItemForm() {
    var form = document.querySelector(".js-add-item-form");
    var tableBody = document.querySelector(".js-items-tbody");
    var toastElement = document.querySelector(".js-item-toast");
    var liveRegion = document.getElementById("item-updates-live-region");

    if (!form || !tableBody) {
        return;
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        var itemNameInput = document.getElementById("id_item_name");
        var quantityInput = document.getElementById("id_quantity");
        var priceInput = document.getElementById("id_price");
        var addedByInput = document.getElementById("id_added_by");

        if (!itemNameInput || !quantityInput || !priceInput || !addedByInput) {
            return;
        }

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        var itemName = itemNameInput.value.trim();
        var quantity = quantityInput.value.trim();
        var price = priceInput.value.trim();
        var addedBy = addedByInput.value.trim();

        if (!itemName || !quantity || !price || !addedBy) {
            return;
        }

        var row = document.createElement("tr");
        row.innerHTML =
            "<td>" + escapeHtml(itemName) + "</td>" +
            "<td>" + escapeHtml(quantity) + "</td>" +
            "<td>" + escapeHtml(addedBy) + "</td>" +
            "<td>£" + escapeHtml(price) + "</td>";

        tableBody.appendChild(row);

        itemNameInput.value = "";
        quantityInput.value = "1";
        priceInput.value = "";

        if (liveRegion) {
            liveRegion.textContent = "Item \"" + itemName + "\" was added.";
        }

        if (toastElement && typeof bootstrap !== "undefined" && bootstrap.Toast) {
            var toastInstance = bootstrap.Toast.getOrCreateInstance(toastElement);
            toastInstance.show();
        }

        if (window.fetch) {
            var actionUrl = form.getAttribute("action") || window.location.href;
            var payload = {
                item_name: itemName,
                quantity: quantity,
                price: price,
                added_by: addedBy
            };

            fetch(actionUrl, {
                method: form.getAttribute("method") || "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify(payload),
                keepalive: true
            }).catch(function () {
                // Network errors are ignored in this demo interaction.
            });
        }
    });
}

// Initialize a simple countdown for the group buy deadline on the detail page
function initDeadlineCountdown() {
    var countdownElement = document.getElementById("groupbuy-countdown");
    if (!countdownElement) {
        return;
    }

    var deadlineValue = countdownElement.getAttribute("data-deadline");
    if (!deadlineValue) {
        return;
    }

    var deadline = new Date(deadlineValue);
    if (isNaN(deadline.getTime())) {
        return;
    }

    function updateCountdown() {
        var now = new Date();
        var diff = deadline.getTime() - now.getTime();

        if (diff <= 0) {
            countdownElement.textContent = "This group buy has closed.";
            window.clearInterval(intervalId);
            return;
        }

        var totalSeconds = Math.floor(diff / 1000);
        var days = Math.floor(totalSeconds / 86400);
        var remainingSeconds = totalSeconds - days * 86400;
        var hours = Math.floor(remainingSeconds / 3600);
        remainingSeconds = remainingSeconds - hours * 3600;
        var minutes = Math.floor(remainingSeconds / 60);

        var parts = [];
        if (days > 0) {
            parts.push(days + "d");
        }
        parts.push(hours + "h");
        parts.push(minutes + "m");

        countdownElement.textContent = "Time remaining: " + parts.join(" ");
    }

    updateCountdown();
    var intervalId = window.setInterval(updateCountdown, 60000);
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Validate that the chosen deadline on the create group buy page is in the future
function initCreateGroupBuyForm() {
    var deadlineInput = document.getElementById("id_deadline");
    var errorElement = document.getElementById("deadline-error");

    if (!deadlineInput || !errorElement) {
        return;
    }

    var form = deadlineInput.form;

    function getSelectedDeadline() {
        if (!deadlineInput.value) {
            return null;
        }

        var candidate = new Date(deadlineInput.value);
        if (isNaN(candidate.getTime())) {
            return null;
        }

        return candidate;
    }

    function showDeadlineError(message) {
        errorElement.textContent = message;
        errorElement.style.display = "";
        deadlineInput.classList.add("is-invalid");
    }

    function clearDeadlineError() {
        errorElement.textContent = "";
        errorElement.style.display = "none";
        deadlineInput.classList.remove("is-invalid");
    }

    function validateDeadline() {
        var selectedDeadline = getSelectedDeadline();
        if (!selectedDeadline) {
            clearDeadlineError();
            return true;
        }

        var now = new Date();

        if (selectedDeadline.getTime() <= now.getTime()) {
            showDeadlineError("Please choose a deadline in the future.");
            return false;
        }

        clearDeadlineError();
        return true;
    }

    deadlineInput.addEventListener("change", validateDeadline);
    deadlineInput.addEventListener("input", validateDeadline);

    if (form) {
        form.addEventListener("submit", function (event) {
            var isValidDeadline = validateDeadline();
            if (!isValidDeadline) {
                event.preventDefault();
                deadlineInput.focus();
            }
        });
    }
}
<<<<<<< HEAD
function joinGroupBuy(id, quantity) {
    var normalizedQuantity = quantity || 1;
    var csrfToken = getCsrfToken();

=======

function joinGroupBuy(id, quantity) {
    var normalizedQuantity = quantity || 1;
    var csrfToken = getCsrfToken();

>>>>>>> 78138d515319c880d41da4a0f85c4ed5f3108918
    return fetch("/groupbuy/" + id + "/join/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "quantity=" + encodeURIComponent(normalizedQuantity)
    }).then(function (response) {
        if (!response.ok) {
            throw new Error("Join request failed");
        }

        alert("Joined!");
        window.location.reload();
    }).catch(function () {
        alert("Could not join this group buy right now.");
    });
}

function getCsrfToken() {
    var cookieString = document.cookie || "";
    var cookiePairs = cookieString.split(";");

    for (var index = 0; index < cookiePairs.length; index += 1) {
        var rawCookie = cookiePairs[index].trim();
        if (!rawCookie) {
            continue;
        }

        if (rawCookie.indexOf("csrftoken=") === 0) {
            return decodeURIComponent(rawCookie.substring("csrftoken=".length));
        }
    }

    return "";
}

