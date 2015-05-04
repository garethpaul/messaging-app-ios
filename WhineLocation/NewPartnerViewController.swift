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

        let partner = self.partnerNumber.text
        let digitsSession = Digits.sharedInstance().session()
        let userId = digitsSession.userID
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

