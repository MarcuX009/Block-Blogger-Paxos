class Queue:
    def __init__(self):
        self.requests = []
        # each index: [POST username title content]

    def append(self, new_request):
        # verify the type of object you're getting - must be a tuple of two integers
        assert isinstance(new_request, str)
        
        if len(new_request) == 4:
            # that means we have a full (LC_time, LC_id, RECIPIENT, AMOUNT)
            pass

        self.requests.append(new_request)

        # custom comparator function, first sorts by 
        # x[0] (first element in tuple, which is lamport time)
        # then sorts by
        # x[1] (second element in tuple, which is process id to break ties)
        # self.requests.sort(key = lambda x: (x[0], x[1]) )
    
    def isEmpty(self):
        if self.size() == 0:
            return True
        return False

    def size(self):
        return len(self.requests)
    
    def pop(self):
        return self.requests.pop(0)

    def peek(self):
        return self.requests[0]
    
    def __str__(self):
        return str(self.requests)
    

if __name__  == '__main__':
    q = Queue()
    q.append("POST username title content")
    userinput = input()
    q.append(userinput)
    print(q)

    # print(q)






