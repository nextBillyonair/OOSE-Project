#import "React/RCTBridgeModule.h"
#import "React/RCTEventEmitter.h"

@import MultipeerConnectivity;

@interface RCTMultipeerConnectivity : RCTEventEmitter <RCTBridgeModule, MCNearbyServiceBrowserDelegate, MCNearbyServiceAdvertiserDelegate>

@property (nonatomic, strong) NSMutableDictionary *peers;
@property (nonatomic, strong) MCPeerID *peerID;
@property (nonatomic, strong) MCNearbyServiceBrowser *browser;
@property (nonatomic, strong) MCNearbyServiceAdvertiser *advertiser;

@end
