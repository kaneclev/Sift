# Core Concepts of the Sift Language
### Targets, The URLs we want
- the `targets` keyword specifies the URLs that we are going to be targeting and retrieving data from. For each target defined under the `targets` keyword, there will be associated actions that Sift will commence  


***Syntax***  
```
targets: [ <url_alias_1>: "url_1", <url_alias_2>: "url_2"]
```
***Rules***   
No two targets may have the same alias. That is, `url_1` and `url_2` may have the same URL *value*, but the alias to refer to that value must differ.

##### Defining actions for the URL Aliases

Actions, or data retrieval and parsing, are defined on the previously defined targets using the following syntax:
```
<url_alias_1>: {
    <action_1>;
    <action_2>;
    ...
}
```
**Note**: Each action statement must be ended with a semicolon.



So, the actions for a particular URL are contained within the braces. 

### Actions on a target
There are many sift actions that can be performed on a URL target, from retrieval,
to status code testing, to conditionals, to looping. 

#### Retrieving data with the `request` keyword
In Sift, the 'scraping' aspect, or the actual retrieval via HTTP of the HTML or CSS content, is implicit, and need not be stated. Once a target is defined, filtering and finding actions on a URL are assumed to be performed on the retrieved data; that is, once a target is defined, you can use the `request` keyword without explicitly calling any http `get` method. 

Sift handles all the requests behind the scenes, and if a request fails, it is assumed that the reason for the fair is either user-related (i.e., the wrong URL), or there is something sift simply cannot bypass (re-captcha, bot detection, etc.). 
In these cases, Sift will always report its best estimate of why the request failed. 

The `request` keyword is used to get content from the site. `request` may be paired with multiple filters, or none at all. 
###### Syntax
`request` must be paired with a target, in the manner described in "Defining actions for the URL Aliases". 
Below is an example of simply grabbing all the site content available from a get request and doing nothing with it.
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request;
}
```
***Note***: All statements using the `request` keyword necessarily make a request to the page for the content. In order to manipulate the contents that were once retrieved, by filtering or saving or otherwise, use the `codename` keyword defined in [[#Defining references to retrieved content with the `codename` keyword |the next section]]

For more examples on how we can filter or store references to the data retrieved from the implicit request by the `request` keyword, see the following sections: 
- [[#Filtering data with the `filter` keyword]]
- [[#`request` and `filter` operations and qualifiers]]
- [[#Combining qualifiers/filters in one action]]
#### Defining references to retrieved content with the `codename` keyword

####### `<statement> | codename <alias>`  
`codename` defines an alias for the content that the previous statement just retrieved.
It is similar to the 'equals' operator; in simpler terms, think of the 'codename' at the end of the statement as saying: "We are going to call the content we just grabbed by the codename \<alias>". In future statements, you can then reference that content by the alias defined after `codename`. 

Be sure to note that the `codename` keyword is preceded by the 'pipe' character `|`,
as if we are 'piping' the content retrieved from the previous sift statement to the `codename` keyword.

The example below shows using the codename keyword to sift *all* content from the "Ebay" target: 
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request | codename all_content;
}
```

`all_content` then references all of the content retrieved from the site, since there are no filters or additional operators on the `request` keyword. 

It should be noted that `codename` is for declaring new content; in future sections like [[#Defining references to retrieved content with the `codename` keyword|referencing previously defined content]]
we will define how to reference predefined content when we use keywords like `using` and `filter`

### Getting the data you want

#### Specifying the relevant content

##### `as` keyword
The `as` keyword defines the content type we are grabbing and filtering on. 

In the context of a `request` statement, the `as` keyword specifies the *content type* we are referencing.
`as <content>`: Where `content` is the type of page content to retrieve, such as `html`, `css`, `js`, etc.

It should be noted that `as` is *not* a required keyword **when used in a request statement**, and can be left out. The only caveat here, is that if `as` is not specified, and the filters used after the request (see:  [[#`request` and `filter`operations and qualifiers|sift and filter operations section]]) are too vague, `request` may retrieve data from CSS and JS content as well.  

*Example*:  
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request as html | codename html_content;
}
```
Without other filters like `tag` or `attribute` or otherwise, the above statement is retrieving all *html* content from the site, and storing it in the `codename` html_content, which refers to the html content that was just retrieved in the statement before the pipe symbol. 

Below is an example using the `as` keyword with the reserved words `js` and `css`:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request as js | codename js_content;
    request as css | codename css_content;
}
```

The above example has two actions: retrieving all JavaScript content from the Ebay target, and storing it as `js_content`, and retrieving all CSS content from the Ebay target, and storing it as `css_content`. 

*Note*: `html`, `js`, `css` are reserved words in the Sift language and may only be used after a `request` statement, used for specifying the relevant content type for that particular request. 
#### Filtering data with the `filter` keyword
Using the `filter` keyword and any of the operations or qualifiers defined in the [[#`request` and `filter`operations and qualifiers|sift and filter operations section]] allows you to filter down just the data you want from the data retrieved using the `request` keyword. 

`filter` operations will happen in the same block as `request` operations, and must reference some `codename` which was already assigned to some data by a previous `request` or `filter` operation.

###### Syntax
`filter` operations occur in a braced block, with the syntax
`filter <alias_to_filter> as { <actions> } | <filtered_alias>`

Consider the following example for scraping CPU listings from eBay:
```
targets = [ CPUs: "https://www.ebay.com/b/CPUs-Processors/164?Brand=AMD&Condition=New&LH_ItemCondition=3000%7C1500&rt=nc&mag=1"]
CPUs: {

    request as html | codename all_html;

    // get the listings

    filter all_html as {
        tags {"div"} with attributes {"class": "s-item__info clearfix"}
       
    } | codename listings;
```

Notice in the above example, we are using the filtering operations present after the `request` keyword and those described in [[#`request` and `filter`operations and qualifiers|'filter operations and qualifiers']] inside the `filter ... as` block. 

The `filter ... as` block allows more precise, compound filtering statements. 

Furthermore, nested `filter ... as` blocks are supported in Sift, for more complex filtering statements:
```
targets = [ CPUs: "https://www.ebay.com/b/CPUs-Processors/164?Brand=AMD&Condition=New&LH_ItemCondition=3000%7C1500&rt=nc&mag=1"]
CPUs: {

    request as html | codename all_html;

    // get the listings

    filter all_html as {
        tags {"div"} with attributes {"class": "s-item__info clearfix"} | codename listing_details,
        filter listing_details as {
	        tags "h3" with attributes {"class": "s-item__title"}
        } | codename titles,
       
    } | codename listings;
```

#### How Sift Views Different Lists

###### `[]`: the or-list

For the all the `request`-related filtering keywords described earlier, when specified in list form, these are automatically ***or*** statements.

(Note: The `targets` list is an exception. )

That is, when we filter with the `attributes` keyword in list form, like:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request attributes ["class": "paginate", "href"] as html | codename paginate_content;
}
```

This will include all elements which have the attribute "class=paginate" **or** the attribute "href" (regardless of the value associated with the href attribute), not necessarily both. 


###### `{}`: the and-list
The `{}` keyword is used within lists of attributes or tags to specify that *both properties must be present for an element to be accepted.* 
(Note:  'action' blocks are an exception (i.e., `Ebay: {}`, `filter ... as: {}`))

Suppose we are only interested in elements which contain *both* "href" *and* "class=paginate"; in this case, we can use the `{}` container rather than the `[]` container, to tell sift to only gather elements which contain *both* attributes.

Example:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request attributes {"class": "paginate", "href"} as html | codename paginate_content;
}
```
The above block will retrieve all elements which have **both** the "class=paginate" attribute **and** the "href" attribute. 

The example below combines a `with` keyword to be even more specific:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request tags ["div", "li"] with attributes {"class": "paginate", "href"} as html | codename paginate_content;
}
```
The above block will retrieve all elements which have the tags "div" **or** "li" (due to the or-list) which also have both the "class=paginate" attribute **and** the "href" attribute. 

#### `request` and `filter` operations

##### `tags` keyword
The `tags` keyword is used on HTML content as a filtering mechanism. It can either be in the form of a simple string, i.e.:

```
tags "div"
``` 
or it can be in the form of an or-list of tags, like:
```
tags ["div", "li", "td", "tr"]
```
(**What is an or-list?** See the [[#Combining qualifiers/filters in one action|combining qualifiers/filters in one action]] section for more details)

Used in conjunction with the `request` keyword, this would work to grab all HTML elements which have the tags in the specified list or with the specified string. 

*Examples*:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request tags "div" as html | codename html_div_content;

}
```
The above example is fetching all elements with the 'div' tag from *only* the html content of the URL. 

```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request tags ["div", "li"] as html | codename html_div_li_content;
}
```
The above example is fetching all elements with **the 'div' *or* the 'li' tag** from *only* the html content of the URL.


##### `attributes` keyword
The `attributes` keyword is used to define a filter much like the `tags` keyword. If `attributes` is used with a string or list on a `request` statement with `from html`, it will only retrieve the elements with those attributes. 

Because HTML attributes are paired with an associated value, like `href=www.google.com`, 
you may filter two ways:

1. Without a specific value attached to the attribute, like:
    ```
    targets: [ Ebay: "www.ebay.com"]
    Ebay: {
        request attributes ["class", "href"] as html | codename paginate_content;
    }
    ```
    Which would retrieve all elements which contain **the "class" *or* the "href" attributes**
2. With a specific value attached to the attribute, with the form:
    ```
    targets: [ Ebay: "www.ebay.com"]
    Ebay: {
        request attributes ["class": "paginate", "href": "next_page"] as html | codename paginate_content;
    }
    ```
    Which would retrieve all elements which contain **the "class" attribute which is equal to "paginate" *or* the "href" attribute which is equal to "next_page"**.


##### `text` keyword
Much like `attributes` and `tags`, the `text` keyword acts as a filter, but applies to the text within a particular HTML element. Its usage is the same as the `attributes` and `tags` qualifiers.

By default, the `text` keyword matches the **exact** text between the tags. 

Example:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request text ["google", "yahoo"] as html | codename text_content;
}
```
The above will retrieve all elements with the text "google" or "yahoo" in them (to be clear, in between the tags, not as a property of any attribute)

##### the `containing` modifier
The `containing` modifier offers a more flexible way to find particular HTML elements by loosening the matching rules for filters like `text`, `attributes`, or `tags`.

When we apply the `containing` modifier to the properties of a specified filter, like:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request text [containing "google", containing "yahoo"] as html | codename text_content;
}
```
We are effectively retrieving any elements which have text which *contains* "google" **or** contains "yahoo". 

Aside from the `text` keyword, we can also apply the `containing` keyword to `tags` keywords and `attributes` keywords.

See the following example:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request tags containing "d" as html | codename d_tag_content;
    request attributes containing "h" as html | codename h_attr_content;
}
```
In the above example, we first sift (which, recall, is making a GET request) all tags which contain "d", including any tags like "body", "div", etc. from the html content and store it as codename `d_tag_content`, and in the second statement, we sift all attributes which contain "h", such as "href" or "hidden".   

It should be noted that in the above example, when we use `containing` on the `attributes` keyword, we are 
referring to the **attribute name itself**, and not the assigned value for that attribute name. For clarity,
below is an example describing how we can apply the `containing` keyword to the value of the attribute itself:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request attributes "href": containing "google" as html | codename h_attr_content;
}
```
The above block grabs all elements which have an "href" tag, but only the ones whose href points to some URL containing "google". An accepted element might look like:

```
<div href=www.google.com/search>Google Search</div>
```

#### Combining qualifiers/filters in one action
For most cases, if we want specific types of elements, we will want to filter by both tag and attribute to get what we want. 

In this case, Sift supports compound statements which will allow for more precise filtering. 

There are useful keywords for logically defining how to filter with the `request` statement. 

##### `with` keyword
If we want `request` to grab all elements with a particular set of tags, such that those elements also contain a particular set of attributes, we can use the `with` keyword.

Below is an example of getting all elements with the 'div' tag, *and* the 'class=paginate' attribute:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request tags "div" with attributes ["class": "paginate"] as html | codename paginate_content;
}
```

We can also reverse the order:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request attributes ["class": "paginate"] with tags "div" as html | codename paginate_content;
}
```
Which effectively does the same thing as the first example.


##### `exclude` keyword
The `exclude` keyword can be used in a `request` statement alongside all other keywords in an effort to exclude all elements with certain attributes or tags. 

The `exclude` keyword takes two following 'arguments'; the type to exclude (`tags`, `attributes`, `text`, etc.), and the content associated with those keywords (like a particular set of tags or attributes or text)

Syntactically, this will usually come after some set of filtering options using `with`, or `attributes`, or `tags`, or all three. 
The `exclude` keyword uses the same types of identifiers to identify which elements to exclude as the `attributes` and `tags` keyword does. 

See the following example, where we want all elements which contain the "href" attribute, except for those which have a "li" tag:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request attributes "href" exclude tags "li" as html | codename href_without_li_tags;
}
```

The `exclude` keyword can also reference a list of characteristics to exclude, either in the form of an `or-list` or an `and-list`.

Here's a more complex example, filtering by multiple types and using a list for the exclude statement:
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request attributes {"class": "paginate", "href"} exclude [ tags ["li", "tr"], attributes ["href": "www.bing.com"] ] as html | codename paginate_content;
}
```
The block above does a few things:
1. We get all elements with the attributes "class=paginate" **and** "href"
2. We exclude all elements with the tag "li" or the tag "tr"
3. We exclude all elements with the attributes "href=www.bing.com" *regardless of whether or not the element has the tag "li" or "tr", since the exclude statement is using an `or-list`*

For completeness, below is an example where we do not filter by any attributes or tags to begin with, but simply exclude certain elements using the `and-list`
```
targets: [ Ebay: "www.ebay.com"]
Ebay: {
    request exclude { tags ["tr", "td"], attributes "col" } as html | codename all_content_excluding;
}
```
The above block sifts all of the content at first, before excluding all elements which fit the following:
If the element **both**:
- has the tag "tr" *or* "td", **and**
- has the attribute "col"
it is not included. All other elements are stored as `all_content_excluding`. 

