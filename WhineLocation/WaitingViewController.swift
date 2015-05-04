
import UIKit
import Alamofire
import DigitsKit

class WaitingViewController: UIViewController {
    @IBOutlet var spinner: UIActivityIndicatorView!
    @IBOutlet var waitingText: UIImageView!
    override func viewDidLoad() {
        super.viewDidLoad()
        check()
    }

    @IBAction func refreshBtnClick(sender: AnyObject) {
        check()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    func check(){
        //
        self.spinner.hidden = false
        self.waitingText.hidden = true

        let delayTime = dispatch_time(DISPATCH_TIME_NOW,
            Int64(2 * Double(NSEC_PER_SEC)))
        dispatch_after(delayTime, dispatch_get_main_queue()) {

            let userId = Digits.sharedInstance().session().userID
            let userPhoneNumber = Digits.sharedInstance().session().phoneNumber
            Alamofire.request(.POST, getInfo("waitingUrl"), parameters: ["userId": userId, "phoneNumber": userPhoneNumber]).responseJSON { (req, res, json, error) in
                if (error != nil) {
                    println("Error: \(error)")
                } else {
                    var json = JSON(json!)
                    if let match = json["match"].string {
                        if match == "True" {
                            // there is now a match
                            self.performSegueWithIdentifier("NavigationViewController", sender: self)
                        }
                    }
                }
            }
            self.spinner.hidden = true
            self.waitingText.hidden = false
        }
    }

}

