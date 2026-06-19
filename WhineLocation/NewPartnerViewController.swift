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
    private var partnerRequest: Request?
    private var isPartnerViewActive = false
    private var partnerViewGeneration = 0

    override func viewWillAppear(animated: Bool) {
        super.viewWillAppear(animated)
        isPartnerViewActive = true
        partnerViewGeneration += 1
    }

    override func viewWillDisappear(animated: Bool) {
        super.viewWillDisappear(animated)
        isPartnerViewActive = false
        partnerViewGeneration += 1
        partnerRequest?.cancel()
        partnerRequest = nil
    }

    @IBAction func phoneEditingDidBegin(sender: AnyObject) {
        applyPartnerNumberPrefixIfNeeded()
    }

    @IBAction func findPartnerBtn(sender: AnyObject) {

        guard let partner = normalizedPartnerNumber(self.partnerNumber.text),
            let userId = currentDigitsUserID(),
            let digitsSession = Digits.sharedInstance().session() else {
                return
        }
        let userPhoneNumber = digitsSession.phoneNumber
        partnerRequest?.cancel()
        partnerRequest = nil
        let requestGeneration = partnerViewGeneration

        let request = Alamofire.request(.POST, getInfo("newpartnerUrl"), parameters: ["userId": userId, "partner": partner, "userPhoneNumber": userPhoneNumber]).validate(statusCode: 200..<300)
        partnerRequest = request
        request.responseJSON { (req, res, json, error) in
            dispatch_async(dispatch_get_main_queue()) {
                guard self.partnerRequest === request else {
                    return
                }

                self.partnerRequest = nil
                guard self.isPartnerViewActive &&
                    requestGeneration == self.partnerViewGeneration &&
                    error == nil else {
                        return
                }

                self.performSegueWithIdentifier("waiting", sender: self)
            }
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        // only numeric
        partnerNumber.keyboardType = UIKeyboardType.DecimalPad
    }

    func applyPartnerNumberPrefixIfNeeded() {
        let existingPartnerNumber = partnerNumber.text?.stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet()) ?? ""
        if existingPartnerNumber.characters.count == 0 {
            partnerNumber.text = "+1"
        }
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
