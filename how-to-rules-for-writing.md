# Some guidelines when writing chapters

## What data formats do we accept ?

- We prefer you clone the project and deliver us your text in markdown.
- However if you are not familiar with mdocs and / or markdown you can deliver us a document in .doc(x)
  or .pages with all needed text and screenshots we will convert it to .md for you

## Meta description

Just above the header add a short description that webcrawlers can use.

```` markdown
    ```
    description: |
        A short deescption of a few lines preferable around 150-200 words.
    tags: [beginner, advanced, expert] #Add one of these tags so that reader knows what level of knowledge is required.
    ```
````


## headings and Captialization

Always start with # followed by the name of the chapter starting with a Capital.
After and before the heading keep 1 line open for readability.

Example:

```markdown
# Document title: The first heading should be a level-one heading.

Ideally the same or nearly the same as the filename.

# Chapter 1

## Chapter 2

### Chapter 3
```

---

## Character line limit

Markdown content follows the residual convention of an 80-character line limit.

**Exceptions:**

Exceptions to the 80-character rule include:

- Links
- Tables
- Headings
- Code blocks

When creating lists use `**` before and after so it's in **_bold_**

Example :

```text
- **First** : my first item
- **Second** : my second item
```

## Trailing whitespaces

Don’t use trailing whitespace. Use a trailing backslash to break lines.

**Example:**

```ascii
For some reason I just really want a break here,\
though it's probably not necessary.
```

---

## Add emphasis on a word

When you want to place special emphasis on a word use \` before and after the word
so it looks like `my special word`.

## Tables

Try to avoid tables, lists are preferred over tables.
When you create a table always try to align the text in the table to the left.

This can be doen with :---- as can be seen in next example

| column 1 | column 2 | colunn 3 |
| :------- | :------- | :------- |
|          |          |          |

---

## Adding images

If you like to add images just create a folder under the chapter folder with
the name of your topic and place the `.png` file it. 7. Naming your images. Always
use the following naming convention: `chxx.y-topic-imagename.png`. Where xx is
the chapter number and y is the number of the image within the chapter.

To reference to your image
just add the name as below in your document. mkdocs will find
the image automatically.

`![Example image 33 in chapter 5](ch05.33-image-example){ align=center }`

`_5.33 Example image 33 in chapter 5`

## Code blocks

Always use 4 spaces for code blocks and add what kind of code you used:

**Example:**

````markdown
    ```python
    print("This is a code block")
    ```
````

When creating info blocks always use ???+ info followed with a white line and
the code in a block with 4 spaces

**Example:**

````markdown
???+ info my info block

    ```
    Bla bla my very informative
    block of text
    ```
````
## Ending the Chapter

End the chapter always with a:

## Conclusion

A short conclusion to explain to the readers what they have learned in this
chapter.

## Questions

- Add a list with questions so that the reader can reflect on the topic.

## Useful URL's

- Add a list with useful URLs to point the reader to more info about this topic.

## Links

If you like to add an URL always put the URi between [] followed by the same URi
again between ().
This will make it easy to click the links online but also later to see the URi in
the book.

**Example:**

```markdown
[https://my-urul.com](https://my-url.com)
```

## reference

- [https://google.github.io/styleguide/docguide/style.html](https://google.github.io/styleguide/docguide/style.html)
- [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)
