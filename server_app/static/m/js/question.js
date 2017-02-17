
var addAssociationAndpoint = "/api/add_association"
var questionIdTag = "#question-id";
var searchButtonTag = "#search-button";
var searchInputTag = "#search-input";
var searchResultTag = "#search-results";
var soQuestionId = -1;
var question = null;

$(document).ready(function() {
    soQuestionId = parseInt($(questionIdTag).text());
    init(function(isSucceeded) {
        if (!isSucceeded)
            return;
        updatePage();
    });
})

function init(onInitCompleted) {
    url = getQuestionApiEndPoint(STACKOVERFLOW_IN_ENGLISH, true, false, "activity", "desc").replace(/\{id\}/g, soQuestionId);
    loadHelper(url, function(data) {
        question = data.items[0];
        onInitCompleted(true);
    }, function() {
        onInitCompleted(false);
    })
    $(searchButtonTag).click(function(event) {
        event.preventDefault();
        $(searchResultTag).empty();
        var theQuery = $(searchInputTag).val();
        queryGoogle(theQuery, function(result) {
            if (result == null || result == undefined || result.items == undefined) {
                $(searchResultTag).append('<h3>' + localeManager.notFoundInGogle + '</h3>');
                return;
            }
            createCandidatesForAssociationList(result.items);
        });
    });
}

function updatePage() {
    $("#question-header h2").text(stripHtml(question.title));
    $("#question-body").html(question.body);
    var tags = createTagsDiv(question.tags);
    $("#question-taglist").append(tags);

    updatePrettify();
    updateSearchInput();
}

function updatePrettify() {
    [].forEach.call(document.getElementsByTagName("pre"), function(el) {
        el.classList.add("prettyprint");
    });
    prettyPrint();
}

function updateSearchInput() {
    $(searchInputTag).val(stripHtml(question.title));
}

function createCandidateIdsString(items) {
    var ids = "";
    var addedIds = new Array();

    for (index = 0; index < items.length; index++) {
        var skipp = false;
        var item = items[index];
        var id = questionId(item.link);

        if (id < 0)
            continue;

        for (subIndex = 0; subIndex < addedIds.length; subIndex++) {
            if (addedIds[subIndex] == id) {
                skipp = true;
                break;
            }
        }

        if (skipp)
            continue;

        ids += id + ";";
        addedIds.push(id);
    }

    return ids.replace(/;+$/, "");
}

function createCandidatesForAssociationList(items) {
    var ids = createCandidateIdsString(items);
    url = getQuestionApiEndPoint(INTERNATIONAL_STACKOVERFLOW, true, false, "activity", "desc").replace(/\{id\}/g, ids);
    loadHelper(url, function(data) {
            function withContext(soen_id, soint_id) {

                $(".soint-" + soint_id).click(function(event) {
                    event.preventDefault();
                    show(soen_id, soint_id);
                });

                $(".soint-" + soint_id + " .candidate-title a").click(function(event) {
                    event.preventDefault();
                    show(soen_id, soint_id);
                });
            }
            for (index = 0; index < data.items.length; index++) {
                var item = data.items[index];

                var tmp = candidateForAssociationTemplate();
                var template = $(tmp);

                $(template).find(".association-candidate .question-id").text(item.question_id);
                $(template).find(".association-candidate .candidate-title a").text(stripHtml(item.title));
                $(template).find(".association-candidate .candidate-body").html(item.body);
                $(template).find(".association-candidate").addClass("soint-" + item.question_id)
                var tags = createTagsDiv(item.tags);
                $(template).find(".candidate-taglist").append(tags);

                $(searchResultTag).append(template.html());
                withContext(soQuestionId, item.question_id)
            }
            updatePrettify();
        },
        function() {

        });
}

function candidateForAssociationTemplate() {
    return `
    <div>
        <div class="association-candidate">
            <div class="candidate-title">
                <a href="#">
                    <span class="question-id" style="display:none">
                </a>
            </div>
            <div class="candidate-body post-text">
            </div>
            <div class="candidate-bar">
                <div class="candidate-taglist"></div>
                <div class="candidate-stats"></div>
            </div>
            <div class="candidate-menu">
            </div>
        </div>
    </div>
    `
}