#import "RCTMultipeerConnectivity.h"
#import "React/RCTBridge.h"
#import "React/RCTEventDispatcher.h"

@implementation RCTMultipeerConnectivity

@synthesize bridge = _bridge;

RCT_EXPORT_MODULE()

RCT_EXPORT_METHOD(invite:(NSString *)peerUUID callback:(RCTResponseSenderBlock)callback) {
  MCPeerID *peerID = [self.peers valueForKey:peerUUID];
  
  MCSession* session = [[MCSession alloc] initWithPeer:self.peerID securityIdentity:nil encryptionPreference:MCEncryptionNone];
  
  [self.browser invitePeer:peerID toSession:session withContext:nil timeout:30];
  
  callback(@[[NSNull null]]);
}

RCT_EXPORT_METHOD(setPeerId:(NSString* )peerId callback:(RCTResponseSenderBlock)callback) {
  NSLog(@"Set Peer id");
  
  self.peerID = [[MCPeerID alloc] initWithDisplayName:peerId];
  callback(@[[NSNull null]]);
}

RCT_EXPORT_METHOD(advertise:(NSString *)channel data:(NSDictionary *)data) {
  NSLog(@"Start advertising");
  self.advertiser = [[MCNearbyServiceAdvertiser alloc] initWithPeer:self.peerID discoveryInfo:data serviceType:channel];
  self.advertiser.delegate = self;
  [self.advertiser startAdvertisingPeer];
}

RCT_EXPORT_METHOD(browse:(NSString *)channel)
{
  NSLog(@"Start browsing");
  self.browser = [[MCNearbyServiceBrowser alloc] initWithPeer:self.peerID serviceType:channel];
  self.browser.delegate = self;
  [self.browser startBrowsingForPeers];
}

RCT_EXPORT_METHOD(stop:(RCTResponseSenderBlock)callback)
{
  NSLog(@"Stop browsing");
  [self.browser stopBrowsingForPeers];
  self.browser.delegate = NULL;
  self.browser = NULL;

  [self.advertiser stopAdvertisingPeer];
  self.advertiser.delegate = NULL;
  self.advertiser = NULL;

  self.peerID = NULL;
  callback(@[[NSNull null]]);
}

- (instancetype)init {
  NSLog(@"Init");
  self = [super init];
  self.peers = [NSMutableDictionary dictionary];
  return self;
}

- (NSArray<NSString *> *)supportedEvents {
  return @[@"RCTMultipeerConnectivityPeerFound", @"RCTMultipeerConnectivityPeerLost", @"RCTMultipeerConnectivityInviteReceived"];
}

- (void)browser:(MCNearbyServiceBrowser *)browser foundPeer:(MCPeerID *)peerID withDiscoveryInfo:(NSDictionary *)discoveryInfo {
  NSLog(@"Found peer");
  NSLog(@"%@ %@",self.peerID.displayName, peerID);
  if ([peerID.displayName isEqualToString:self.peerID.displayName]) return;

  [self.peers setValue:peerID forKey:peerID.displayName];
  if (discoveryInfo == nil) {
    discoveryInfo = [NSDictionary dictionary];
  }
  NSLog(@"Send peer found");
  [self sendEventWithName:@"RCTMultipeerConnectivityPeerFound"
                               body:@{
                                 @"peer": @{
                                   @"id": peerID.displayName,
                                   @"discoverInfo": discoveryInfo
                                 }
                               }];
}

- (void)browser:(MCNearbyServiceBrowser *)browser lostPeer:(MCPeerID *)peerID {
  if ([peerID.displayName isEqualToString:self.peerID.displayName]) return;
  [self sendEventWithName:@"RCTMultipeerConnectivityPeerLost"
                     body:@{
                            @"peer": @{
                                @"id": peerID.displayName
                                }
                            }];
  [self.peers removeObjectForKey:peerID.displayName];
}

- (void)advertiser:(MCNearbyServiceAdvertiser *)advertiser didReceiveInvitationFromPeer:(MCPeerID *)peerID withContext:(NSData *)context invitationHandler:(void (^)(BOOL accept, MCSession *session))invitationHandler {
  
  NSString *invitationUUID = peerID.displayName;
  invitationHandler(false, NULL);

  [self sendEventWithName:@"RCTMultipeerConnectivityInviteReceived"
                              body:@{
                                @"invite": @{
                                  @"id": invitationUUID
                                },
                                @"peer": @{
                                  @"id": peerID.displayName
                                }
                              }];
}

- (void)session:(MCSession *)session peer:(MCPeerID *)peerID didChangeState:(MCSessionState)state {}

- (void)session:(MCSession *)session didReceiveCertificate:(NSArray *)certificate fromPeer:(MCPeerID *)peerID certificateHandler:(void (^)(BOOL accept))certificateHandler {
  certificateHandler(YES);
}

- (void)session:(MCSession *)session didReceiveData:(NSData *)data fromPeer:(MCPeerID *)peerID {}


- (void)session:(nonnull MCSession *)session didReceiveStream:(nonnull NSInputStream *)stream withName:(nonnull NSString *)streamName fromPeer:(nonnull MCPeerID *)peerID {}


- (void)session:(nonnull MCSession *)session didStartReceivingResourceWithName:(nonnull NSString *)resourceName fromPeer:(nonnull MCPeerID *)peerID withProgress:(nonnull NSProgress *)progress {}


@end
