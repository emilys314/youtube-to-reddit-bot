import pickle

## Two-way Dictionary to keep track of what subreddits have which channels has
## be able to look up both ways
class TwoWayMap(dict):

    def __init__(self):
        self.channelToSubs = {}
        self.subToChannels = {}

    # add a channel to a subreddit
    def add(self, sub, channels):
        self.add_channel(sub, channels)
        self.add_sub(sub, channels)

    # add the subreddit to channel relationship
    def add_channel(self, sub, channels):
        tempchannels = self.subToChannels.get(sub)
        if not tempchannels:        #if empty
           tempchannels = set()
        tempchannels.update(channels)
        self.subToChannels[sub] = tempchannels
#        print(tempchannels)

    # add the channel to subreddit relationship
    def add_sub(self, sub, channels):
        for channel in channels:
            subs = self.channelToSubs.get(channel)
            if not subs:
                subs = set()
            subs.add(sub)
            self.channelToSubs[channel] = subs

    # get list of subreddits a channel is posting to
    def getSubsByUpload(self, upload):
        return self.channelToSubs[upload.channel_id]

    def getChannelsBySub(self, sub):
        return self.subToChannels[sub]

    # remove a channel from a sbureddit
    def remove(self, sub, channels):
        if sub in self.subToChannels:
            self.remove_sub(sub, channels)
            self.remove_channel(sub, channels)

    def remove_channel(self, sub, channels):
        tempchannels = self.subToChannels.get(sub)
        for channel in channels:
            tempchannels.discard(channel)
        if not tempchannels:
            del self.subToChannels[sub]
        else:
            self.subToChannels[sub] = tempchannels

    def remove_sub(self, sub, channels):
        self.printstuff()
        print(sub,channels)
        for channel in channels:
            print(channel)
            if channel in self.channelToSubs:
                subs = self.channelToSubs.get(channel)
                #if sub in subs:
                subs.discard(sub)
                if not subs:
                    del self.channelToSubs[channel]
                else:
                    self.channelToSubs[channel] = subs

    # return a list of channels the subreddit is subscribed to
    # returns error string if subreddit not found
    def list(self, sub):
        if sub in self.subToChannels:
            return self.subToChannels[sub]
        else:
            return "Error! Subreddit not found"

    # save both the maps to a file
    def save(self):
        with open("maps.p", 'wb+') as fp:
            pickle.dump(self.channelToSubs, fp)
            pickle.dump(self.subToChannels, fp)

    # load both maps from the file
    def load(self):
        with open("maps.p",'rb+') as fr:
            try:
                while True:
                    self.channelToSubs = pickle.load(fr)
                    self.subToChannels = pickle.load(fr)
            except EOFError:
                pass


    def printstuff(self):
        print("Map:")
        print("  ",self.channelToSubs)
        print("  ",self.subToChannels)
