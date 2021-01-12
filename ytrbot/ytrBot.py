import praw
from multiprocessing import Process, Queue
import CallbackServer
from TwoWayMap import TwoWayMap
import atexit
import time


def main():
    print()
    reddit = authToReddit()
    videoQueue = startCallbackServer()
    map = loadChannelSubMap()

    print("Starting ytr-bot")
    numCommands = 0
    currentSleepTime = 0
    sleepTimeIncrement = 0.1
    maxSleepTime = 5

    numQueue = 0
    currentSkipIteration = 0
    currentSkipMax = 0
    skipIntervalIncrement = 1
    maxSkipInterval = 10
    while True:
        numQueue = do_video_queue(reddit, videoQueue, map)
        if numQueue == 0 and currentSleepTime <= maxSleepTime:
            currentSleepTime += sleepTimeIncrement
        elif currentSleepTime >= sleepTimeIncrement:
            currentSleepTime -= sleepTimeIncrement
        print("videoQueue:",numQueue)

        if (currentSkipIteration == 0):
            numCommands = do_reddit_commands(map, reddit)
            print("Commands:",numCommands)
        currentSkipIteration += skipIntervalIncrement
        if (currentSkipIteration > currentSkipMax):
            currentSkipIteration = 0
        if (numCommands == 0 and currentSkipMax <= maxSkipInterval):
            currentSkipMax += skipIntervalIncrement
        elif currentSkipMax >= skipIntervalIncrement:
            currentSkipMax -= skipIntervalIncrement

        print("Sleeptime:",currentSleepTime,"|","Skipping:",currentSkipMax)
        time.sleep(currentSleepTime)

# login to reddit
def authToReddit():
    print("Authenticating ...",end='')
    reddit = praw.Reddit('user', user_agent='Prawn:ytr-test-bot:v0.1 /u/user')
    print(" as {}".format(reddit.user.me()))
    return reddit

def startCallbackServer():
    videoQueue = Queue()       #make serverQueue to communicate
    serverProcess = Process(target=CallbackServer.start, args=(serverQueue,))
    serverProcess.start()
    testAddQueue(videoQueue, "message.htm")
    return videoQueue

def loadChannelSubMap():
    map = TwoWayMap()
    map.load()
    return map

# run bot by checking reddit for commands and checking for new uploads in queue
def run_bot(reddit, queue, map):
    numCommands = do_reddit_commands(map, reddit)
    numQueue = do_video_queue(reddit, queue, map)

    return (numCommands, numQueue)

# Check reddit inbox for commands by moderators and do them
def do_reddit_commands(map, reddit):
    commands = check_reddit_pms(reddit)       #list of new commands
    changed = False
    for command in commands:
        print("Executing command:",command)
        if command[0] == "ADD":
            map.add(command[1], command[2:])
            #TODO: curl subscription to hub server
            changed = True
        if command[0] == "REMOVE":
            map.remove(command[1], command[2:])
            changed = True
        if command[0] == "LIST":
            subList = map.list(command[1])
            print("LIST",subList)
            #TODO: reply with subList to user
    if changed:
        map.save()
    return len(commands)

def do_video_queue(reddit, queue, map):
    numQueue = queue.qsize()
    while not queue.empty():
        upload = queue.get()        #get objects in serverQueue
        subsToUploadTo = map.getSubsByUpload(upload)
        for sub in subsToUploadTo:
            postUpload(reddit, sub, upload)
    return numQueue

# check and parse unread messages of account
# return list of commands in format ["COMMAND", "subreddit", "channel1", "channel2", ...]
def check_reddit_pms(reddit):
    commands = []
    print("Checking messages...")
    for message in reddit.inbox.unread(limit=2):
        message.mark_read()
        #print("New message from",message.author,"about",message.subject,"saying:",message.body)
        if len(message.subject.split()) >= 2:
            order = message.subject.split()[0].upper()
            subreddit = message.subject.split()[1]
            if message.author in reddit.subreddit(subreddit).moderator():
                if order == "LIST" or order == "ADD" or order == "REMOVE":
                    command = [order,subreddit]
                    command.extend(message.body.split())
                    commands.append(command)
                else:
                    print("ERROR: Invalid command",order)
            else:
                print("ERROR: u/",message.author,"has no moderator privilages for r/",subreddit)
        else:
            print("ERROR: not enough arguments in command:",message.subject)
    #print("Commands:",commands)
    return commands

# subscribe to pubsubhubbub upload notificiations for channel
def subscribeTo(channel):
    # TODO: curl(channel)
    pass


def testAddQueue(queue, file):
    text = open(file, 'r').read()
    upload = CallbackServer.Upload(text)
    queue.put(upload)
    print("test add queue complete for:",upload)

# post upload to a subreddit
def postUpload(reddit, subreddit, upload):
    print("Posting link to", subreddit)
    subreddit = reddit.subreddit(subreddit)
    try:
        subreddit.submit(upload.title, url=upload.url, resubmit=False, flair_text=upload.author)
    except:
        print("ERROR: Could not post:",upload.title,"by:",upload.author)

# post self post to a subreddit
def postSelf(reddit, subreddit, title, desc):
    print("Posting to reddit")
    subreddit = reddit.subreddit('')
    subreddit.submit('Hello', selftext='desc')


if __name__ == '__main__':
    main()
