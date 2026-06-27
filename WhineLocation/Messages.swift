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
private var readStatePublicationGeneration = 0

func setRead(data: AnyObject, userId: String) {
    defaults.setObject(data, forKey: userId)
}

func compareRead(data:AnyObject!) {
    guard let userId = currentDigitsUserID(),
        let remoteReadState = data as? NSArray else {
            return
    }

    readStatePublicationGeneration += 1
    let publicationGeneration = readStatePublicationGeneration

    let localReadState = defaults.objectForKey(userId) as? NSArray ?? NSArray()

    if localReadState != remoteReadState {
        let request = Alamofire.request(.POST,
            getInfo("pulseListReadUrl"),
            parameters:["data": remoteReadState, "userId": userId],
            encoding: .JSON).validate(statusCode: 200..<300)
        request.responseJSON { (req, res, json, error) in
            guard error == nil else {
                return
            }

            guard publicationGeneration == readStatePublicationGeneration else {
                return
            }

            setRead(remoteReadState, userId: userId)
        }
    }
} // end compare read

func currentDigitsUserID() -> String? {
    if let session = Digits.sharedInstance().session() {
        return normalizedDigitsUserID(session.userID)
    }

    return nil
}

func normalizedDigitsUserID(userID: String?) -> String? {
    guard let userID = userID else {
        return nil
    }

    let trimmedUserID = userID.stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())
    if trimmedUserID.characters.count == 0 {
        return nil
    }

    return trimmedUserID
}
