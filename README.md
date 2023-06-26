<H1> CS171 Final Project, June 2023</H1>
<H2> Author: Wenjin Li, An Cao </H2>
<H2> Attention students taking this class or studying this subject: kindly refrain from simply copying and utilizing this code for your submission. Your instructor will be able to detect this. Please refer to the 'LICENSE' for additional restrictions. </H2>

Note: `save` and `load` commands are only used when you want to save or recover the server info from disk manually, the server will auto-recover from the majority's information when it joins the distributed system.

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

