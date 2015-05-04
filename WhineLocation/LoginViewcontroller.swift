//
//  ViewController.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 3/28/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import UIKit
import DigitsKit

import Parse

class LoginViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    @IBAction func phoneBtnClick(sender: AnyObject) {
        let digitsAppearence = DGTAppearance()
        digitsAppearence.backgroundColor = toColor("0350a2")
        digitsAppearence.accentColor = toColor("0661be")
        let digits = Digits.sharedInstance()

        digits.authenticateWithDigitsAppearance(digitsAppearence, viewController: nil, title: nil) { (session, error: NSError!) -> Void in
            if session != nil {
                let user = User()
                user.New(session.userID, phoneNumber: session.phoneNumber)
                PFInstallation.currentInstallation().setObject(session.userID, forKey: "user")
                PFInstallation.currentInstallation().saveEventually({ (saved, error) -> Void in
                    
                })
                self.performSegueWithIdentifier("NewPartner", sender: self)
            }
            else {
                self.performSegueWithIdentifier("NewPartner", sender: self)
            }
        }

    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}

