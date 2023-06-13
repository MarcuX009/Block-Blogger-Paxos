# CS171 Final Project, June 2023
# Blog.py
# Author: Wenjin Li, An Cao
from ast import literal_eval

class Post:
    def __init__(self, username, title, content):
        self.authorNtitle = (username, title)
        self.content = content

        self.comment = dict()

    def __str__(self): # need add print comments
        return f" Author: {self.authorNtitle[0]}\n  \
                   Title: {self.authorNtitle[1]}\n\
                 Content: {self.content}"

    def to_dict(self):
        comment_str = {str(k): v for k, v in self.comment.items()}
        return {
            'authorNtitle': self.authorNtitle,
            'content': self.content,
            'comment': comment_str
        }
    
    @classmethod
    def from_dict(cls, data):
        post = cls(*data['authorNtitle'], data['content'])
        post.comment = {
            literal_eval(key): value 
            for key, value in data['comment'].items()
        }
        return post
    
    def get_authorNtitle(self):
        return self.authorNtitle
    
    def get_content(self):
        return str(self.content)
    
    def get_comment(self):
        print(f"Looking for the comment in {self.authorNtitle[0]}---{self.authorNtitle[1]}...")
        if len(self.comment) == 0:
            print("\tThis post has no comment yet.\n")
            return
        for each_comment in self.comment:
            print(f"\t{each_comment[0]}: {each_comment[1]}") 
        print()
    
    def check_comment_exist(self, follower, new_content):
        if (follower,new_content) in self.comment:
            return True
        return False

    def add_comment(self, follower, new_content):
        if (follower,new_content) in self.comment:
            print(f"Error! This comment already existed:\n\t{follower}: {new_content}\n")
            return
        self.comment[(follower,new_content)] = True

class Blog:
    def __init__(self):
        self.blog_list = dict()

    def to_dict(self):
        blog_list_dict = {
            authorNtitle: post.to_dict()
            for authorNtitle, post in self.blog_list.items()
        }
        return {
            'blog_list': blog_list_dict
        }

    @classmethod
    def from_dict(cls, data):
        blog = cls()
        blog.blog_list = {
            authorNtitle: Post.from_dict(post_data)
            for authorNtitle, post_data in data['blog_list'].items()
        }
        return blog

    def makeNewPost(self, new_post):
        assert isinstance(new_post,Post)
        assert isinstance(new_post.get_authorNtitle(), tuple)

        if new_post.get_authorNtitle() in self.blog_list:
            print(f"Error on making a new post on {new_post.get_authorNtitle()}: ")
            print("\tthis author already has a post with the same title!\n")
            return
        self.blog_list[new_post.get_authorNtitle()] = new_post

    def get_posts_by_author(self, author):
        assert isinstance(author, str)
        found = False
        print(f"Looking for all the post from {author}...")
        for authorNtitle, post in self.blog_list.items():
            if author == authorNtitle[0]:
                print(f"\t{authorNtitle[1]}: {post.get_content()}")
                found = True
        if not found:
            print("\tThis user/author has not any post yet!")
        print()

    def get_post(self, authorNtitle):
        assert isinstance(authorNtitle, tuple)

        if authorNtitle not in self.blog_list:
            print(f"Error, Post not found with: \
                   '{authorNtitle[0]}', '{authorNtitle[1]}'")
            return
        return self.blog_list[authorNtitle]

    def check_post_exist(self, authorNtitle):
        assert isinstance(authorNtitle, tuple)

        if authorNtitle not in self.blog_list:
            return False
        return True

    # def size(self):
        # return len(self.blog_list)

    def __str__(self):
        # return [x in self.blog_list for all]
        return str(self.blog_list)

    def view_all_posts(self):
        if len(self.blog_list.keys()) == 0:
            print("\tBLOG EMPTY\n")
            return
        
        print("|author|-------|title|")
        for authorNtitle in self.blog_list:
            print(f"\t{authorNtitle[0]}-------{authorNtitle[1]}")
        # return self.blog_list
        print()


if __name__  == '__main__':
    # POST Marcus Answer_for_the_final_exam ABCDEFG
    # POST CXK JNTM one_more_look_then_boom
    # POST white55kai 55kai's_answer 8910JQKA
    # POST CXK JNTM2 NiGanMa_AiYo
    # POST BananaMan How_to_be_a_Banana theSecretIsEatingMoreBanana
    # POST CXK Aiyoooo JJJJJJJJ
    blog = Blog()
    blog.makeNewPost(Post('Marcus','Answer for the final exam', 'ABCDEFG'))
    blog.makeNewPost(Post('CXK', 'JNTM', 'one_more_look_then_boom'))
    blog.makeNewPost(Post('white55kai', "55kai's_answer", '8910JQKA'))
    blog.makeNewPost(Post('CXK','JNTM2', 'NiGanMa_AiYo'))
    blog.makeNewPost(Post('BananaMan','How_to_be_a_Banana', 'theSecretIsEatingMoreBanana'))
    blog.makeNewPost(Post('CXK','Aiyoooo', 'JJJJJJJJ'))
    # print(blog)
    blog.view_all_posts()
    authorNtitle = ('CXK', 'JNTM')
    print(type(authorNtitle))
    if blog.check_post_exist(authorNtitle):
        if not blog.get_post(authorNtitle).check_comment_exist(follower='No.1',new_content='ikun!'):
                blog.get_post(authorNtitle).add_comment(follower='No.1', new_content='ikun!')
                print(f"SUCCESS created a new COMMENT")
        else:
            print(f"Error! This comment already existed:\n")
    if blog.check_post_exist(authorNtitle):
        if not blog.get_post(authorNtitle).check_comment_exist(follower='No.1',new_content='ikun!'):
                blog.get_post(authorNtitle).add_comment(follower='No.1', new_content='ikun!')
                print(f"SUCCESS created a new COMMENT")
        else:
            print(f"Error! This comment already existed:\n")
    
    
    blog.get_post(('CXK', 'JNTM')).add_comment(follower="bob",new_content="good post!")
    blog.get_post(('CXK', 'JNTM')).add_comment(follower="bob",new_content="good post!")
    
    
    blog.get_posts_by_author("CXK")
    blog.get_posts_by_author("asda")
    
    blog.get_post(('CXK', 'JNTM')).get_comment()
    
    print("Done!")

