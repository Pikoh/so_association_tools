# Introduction

This is a basic plugin that changes the way how associations look like on international Stack Overflows.

There were some [discussions](http://meta.ru.stackoverflow.com/questions/4500/) on Meta Stack Overflow in Russian, that we have to find a better way of adding associations than through an answer on meta. [It was suggested](http://meta.ru.stackoverflow.com/a/4507/6) to add associations in a comment to a question on an international sites.

# Specification 

<sup>\*Specification bellow is a result of discussions on Meta Stack Overflow in Russian and some my personal thoughts. If you think that something is wrong, [let me know](http://meta.ru.stackoverflow.com/questions/ask)!</sup>

The most general part is the extension. The server application would be implemented only in case of the interest from community. For the server we will use our external machine hosted by Hetzner (Ubuntu Server 12.04). According to current server's environment the application could be written only in Python or Go.

1. Browser extension

  1. Transform a comment with an association tag to a box.
  2. Add an "associate" link to user's tools under questions that do not have association. By clicking on the comment menu should expand with the tag inside. After an association has been sent, the comment should automatically transform according 1.1.
  3. Users should have ability to edit or delete an association.

2. Server side application

  1. Statically (array, dic, or any other) store associations and their authors. It will be updated manually by Stack Overflow employees.
  2. Return all associations and authors by an API call.
  3. Statically store a list of suggestions of questions to be associated. (As a metric "most viewed on SOen by a language users" may be used.) It will be updated manually be Stack Overflow employees.
  4. Serve a page with suggested for association questions. One question per page. Right after the question add a manual Google Search "\*.stackoverflow.com", the results should be right under the question.
  5. Serve a page with the list of associated questions ordered by time.


# Current Status

## Supporting Browsers

We are planning to support a few major browsers. As I understood Opera and Firefox have migrated to Chromium open source project. It means that they use the same extension mechanism as Google Chrome. I've tested the extention last time in

- Google Chrome, Mac OS X, v55.0.2883.95 64-bit
- Opera, Mac OS X, v42.0.2393.137 64-bit
- Firefox, Mac OS X, v50.1.0 64-bit

## How To Install

We suggest use an "unpacked" version of the extension right from a folder with the code.

- Chrome: https://developer.chrome.com/extensions/getstarted#unpacked
- Opera: https://dev.opera.com/extensions/testing/
- Firefox: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Your_first_WebExtension#Trying_it_out

## Implementation

At the time of writing, we implemented the basic functionality of the web extension including

- Parsing comments with the association tag. Comments are fetching from SE by API.
- Adding a box if an association is found in comments.
- Adding an "associate" link in the user's mod tools under question body. By clicking on the link the add comment menu is expanded and the association tag automatically put in the text area.

### Association Format

Currently we use the following format

__For Stack Overflow in Russian__

    ассоциация: ссылка_на_вопрос_на_английском
    
For exmaple, `ассоциация:http://stackoverflow.com/questions/3211771/how-to-convert-int-to-qstring`

### Showcase

After adding the extension comments with associations will look like this

![](https://i.stack.imgur.com/heLd6.png)

The second part is the "association" link.

![](https://i.stack.imgur.com/DtoWV.png)

By clicking on which an input field will expand. Add the link to the associated question on Stack Overflow in English and click "Associate".

![](https://i.stack.imgur.com/jWVhh.png)


