package pymontecarlo.input.nistmonte;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Properties;

/**
 * Abstract detector.
 * 
 * @author ppinard
 */
public abstract class AbstractDetector implements Detector {

    @Override
    public void saveLog(File resultsDir, String baseName) throws IOException {
        File logFile = new File(resultsDir, baseName + ".log");

        Properties props = new Properties();
        saveAsProperties(props);

        OutputStream out = new FileOutputStream(logFile);
        props.store(out, "");
        out.close();
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

}
