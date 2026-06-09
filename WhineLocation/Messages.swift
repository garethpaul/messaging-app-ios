//
//  Messages.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 4/7/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import Foundation
import Alamofire
import DigitsKit

let defaults = NSUserDefaults.standardUserDefaults()

func setRead(data: AnyObject) {
    if let userId = currentDigitsUserID() {
        defaults.setObject(data, forKey: userId)
    }
}

func compareRead(data:AnyObject!) {
    guard let userId = currentDigitsUserID(),
        let remoteReadState = data as? NSArray else {
            return
    }

    let localReadState = defaults.objectForKey(userId) as? NSArray ?? NSArray()

    if localReadState != remoteReadState {
        Alamofire.request(.POST,
            "https://requestlabs.appspot.com/whine/pulse/messages/read",
            parameters:["data": remoteReadState, "userId": userId],
            encoding: .JSON)
        setRead(remoteReadState)
    }
} // end compare read

func currentDigitsUserID() -> String? {
    if let session = Digits.sharedInstance().session() {
        return session.userID
    }

    return nil
}


