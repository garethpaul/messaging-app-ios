//
//  ViewController.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 3/28/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import UIKit
import Alamofire
import DigitsKit

class NewPartnerViewController: UIViewController {

    @IBOutlet var findPartnerBtn: UIButton!
    @IBOutlet var partnerNumber: UITextField!

    @IBAction func phoneEditingDidBegin(sender: AnyObject) {
        partnerNumber.text = "+1"
    }

    @IBAction func findPartnerBtn(sender: AnyObject) {

        guard let partner = normalizedPartnerNumber(self.partnerNumber.text),
            let userId = currentDigitsUserID(),
            let digitsSession = Digits.sharedInstance().session() else {
                return
        }
        let userPhoneNumber = digitsSession.phoneNumber

        Alamofire.request(.POST, getInfo("newpartnerUrl"), parameters: ["userId": userId, "partner": partner, "userPhoneNumber": userPhoneNumber]).responseJSON { (req, res, json, error) in
            if (error != nil) {

            } else {
                // error
                self.performSegueWithIdentifier("waiting", sender: self)
            }
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        // only numeric
        partnerNumber.keyboardType = UIKeyboardType.DecimalPad
    }


    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}

func normalizedPartnerNumber(partnerNumber: String?) -> String? {
    guard let partnerNumber = partnerNumber else {
        return nil
    }

    let trimmedPartnerNumber = partnerNumber.stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())
    if trimmedPartnerNumber.characters.count == 0 {
        return nil
    }

    return trimmedPartnerNumber
}
