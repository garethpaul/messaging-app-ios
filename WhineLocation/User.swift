import Foundation
import Alamofire
import DigitsKit

class User {
    // Track

    let bundleID = String(NSBundle.mainBundle().bundleIdentifier!)

    func New(userId: String, phoneNumber: String) {
        Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/user", parameters: ["bundleId": bundleID, "phoneNumber": phoneNumber, "userId": userId])
    }
}
