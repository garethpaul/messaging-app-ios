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
    defaults.setObject(data, forKey: Digits.sharedInstance().session().userID)
}

func compareRead(data:AnyObject!) {
    if let localData: AnyObject! = defaults.objectForKey(Digits.sharedInstance().session().userID) {
        var localArray = [] as NSArray
        if localData != nil {
            localArray = localData as! NSArray
        }
        let localCompare = data as! NSArray

        if localArray != localCompare {

            let parameters : [String: AnyObject] = ["data": data, "userId": Digits.sharedInstance().session().userID]

            Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/pulse/messages/read", parameters:["data": data, "userId": Digits.sharedInstance().session().userID], encoding: .JSON)
            }
            setRead(data)
        } else {
            // all is normal
        } // end else
} // end compare read



