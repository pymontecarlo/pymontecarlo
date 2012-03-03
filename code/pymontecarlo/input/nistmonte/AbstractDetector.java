package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.awt.event.ActionEvent;
import java.io.IOException;
import java.io.StringWriter;
import java.util.Properties;
import java.util.zip.ZipOutputStream;

import pymontecarlo.util.ZipUtil;

/**
 * Abstract detector.
 * 
 * @author ppinard
 */
public abstract class AbstractDetector implements Detector {

    @Override
    public void actionPerformed(ActionEvent e) {
        switch (e.getID()) {
        case MonteCarloSS.FirstTrajectoryEvent:
            reset();
            break;
        default:
            break;
        }
    }



    @Override
    public void reset() {

    }



    /**
     * Saves parameters in a <code>Properties</code> object. This object will be
     * used to create the detector log file.
     * 
     * @param props
     *            properties where to store parameters
     */
    protected void saveAsProperties(Properties props) {

    }



    @Override
    public void saveLog(ZipOutputStream zipOutput, String key)
            throws IOException {
        Properties props = new Properties();
        saveAsProperties(props);

        StringWriter sw = new StringWriter();
        props.store(sw, "");
        ZipUtil.saveStringBuffer(zipOutput, key + ".log", sw.getBuffer());
    }

}
