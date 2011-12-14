package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.AlgorithmClass;

import java.util.Map;

public abstract class AbstractModelExtractor<T extends AlgorithmClass>
        implements ModelExtractor {

    public AbstractModelExtractor(String name, Class<T> clasz,
            Map<String, ? extends T> lut) {

    }

}
