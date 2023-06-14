<H1> CS171 Final Project, June 2023</H1>
<H2> Author: Wenjin Li, An Cao </H2>


Note: `save` and `load` command only used when you want to manually save or recover the server info from disk, server will auto recover from the majority's info when it join the distributed systerm.

|      Commands      |        Use for         |
|:-------------------|:---------------------------------:|
| show               | show all allowing input command |
| info               | show the server status |
| failLink X / fail X  | fail the connection from this server to X=targetServer |
| fixLink X / fix X  | fix the connection from this server to X=targetServer |
| BlockChain or BC   | show the BC in a list  |
| queue              | close the server       |
| save/load               | manually save/load the BC, server info, Blog to/from local disk      |
| exit               | close the server       |
| wait x             | sleep for x second     |
| (empty string)     | do nothing but continue|
|--------------------|----------------------------------|
| POST X Y Z         |  X=sername Y=title Z=content |
| COMMENT X Y Z      | X=TagerUsername Y=TargetTitle Z=comment |
| view all posts         | To view all posts   |
| view posts X         | view all posts from X=TagerUsername   |
| view comments X Y  | view all comments from X=TagerUsername Y=TargetTitle |

