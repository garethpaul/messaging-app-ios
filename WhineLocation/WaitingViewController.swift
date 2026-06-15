
import UIKit
import Alamofire
import DigitsKit

class WaitingViewController: UIViewController {
    @IBOutlet var spinner: UIActivityIndicatorView!
    @IBOutlet var waitingText: UIImageView!
    private var isChecking = false
    private var hasMatched = false
    private var isWaitingViewActive = false

    override func viewDidLoad() {
        super.viewDidLoad()
        check()
    }

    override func viewWillAppear(animated: Bool) {
        super.viewWillAppear(animated)
        isWaitingViewActive = true
    }

    override func viewWillDisappear(animated: Bool) {
        super.viewWillDisappear(animated)
        isWaitingViewActive = false
        finishWaitingCheck()
    }

    @IBAction func refreshBtnClick(sender: AnyObject) {
        check()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    func check(){
        guard !isChecking && !hasMatched else {
            return
        }

        isChecking = true
        self.spinner.hidden = false
        self.waitingText.hidden = true

        let delayTime = dispatch_time(DISPATCH_TIME_NOW,
            Int64(2 * Double(NSEC_PER_SEC)))
        dispatch_after(delayTime, dispatch_get_main_queue()) {
            guard self.isWaitingViewActive else {
                self.isChecking = false
                return
            }

            guard let digitsSession = Digits.sharedInstance().session(),
                let userId = normalizedDigitsUserID(digitsSession.userID) else {
                    self.finishWaitingCheck()
                    return
            }

            Alamofire.request(.POST, getInfo("waitingUrl"), parameters: ["userId": userId, "phoneNumber": digitsSession.phoneNumber]).responseJSON { (req, res, json, error) in
                guard self.isWaitingViewActive else {
                    self.isChecking = false
                    return
                }

                self.finishWaitingCheck()
                guard error == nil, let jsonValue = json else {
                    return
                }

                var responseJSON = JSON(jsonValue)
                if responseJSON["match"].string == "True" {
                    // there is now a match
                    self.hasMatched = true
                    self.performSegueWithIdentifier("NavigationViewController", sender: self)
                }
            }
        }
    }

    private func finishWaitingCheck() {
        self.isChecking = false
        self.spinner.hidden = true
        self.waitingText.hidden = false
    }

}
