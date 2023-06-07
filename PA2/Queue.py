class Queue:
    def __init__(self):
        self.requests = []
    
    def append(self, new_request):
        # verify the type of object you're getting - must be a tuple of two integers
        assert isinstance(new_request, ( tuple ))

        if len(new_request) == 4:
            # that means we have a full (LC_time, LC_id, RECIPIENT, AMOUNT)
            pass


        if len(new_request) == 2:
            # that means we knoy have (LC_time and LC_id) so we will attach R and A as RECIPIENT and AMOUNT
            new_request = (new_request[0], new_request[1], 'R', 'A')
        
        self.requests.append(new_request)

        # custom comparator function, first sorts by 
        # x[0] (first element in tuple, which is lamport time)
        # then sorts by
        # x[1] (second element in tuple, which is process id to break ties)
        self.requests.sort(key = lambda x: (x[0], x[1]) )
    
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
    q.append( (1, 3) )
    print(q)
    # threading.Thread(target=self.receive_messages, args=(client,)).start()
    q.append( (5, 3, 'P2', '$4') )
    q.append( (5, 2) )
    print(q)






